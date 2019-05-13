from utils import detector_utils as detector_utils
from multiprocessing import Queue, Pool
from utils.detector_utils import WebcamVideoStream
import cv2
import tensorflow as tf
import multiprocessing
import time
import datetime
import argparse
import socket
import json

frame_processed = 0
score_thresh = 0.2

# Change thresh amount to adjust smoothing of ROTATE command
delta_thresh = 30
prev_x = 0
prev_y = 0

HOST = '127.0.0.1'
PORT = 31416

# Create a worker thread that loads graph and
# does detection on images in an input queue and puts it on an output queue

def worker(input_q, output_q, midpoint_q, cap_params, frame_processed):
    print(">> loading frozen model for worker")
    detection_graph, sess = detector_utils.load_inference_graph()
    sess = tf.Session(graph=detection_graph)
    while True:
        # print("> ===== in worker loop, frame ", frame_processed)
        frame = input_q.get()
        if (frame is not None):
            # Actual detection. Variable boxes contains the bounding box cordinates for hands detected,
            # while scores contains the confidence for each of these boxes.
            # Hint: If len(boxes) > 1 , you may assume you have found atleast one hand (within your score threshold)

            midpoint_list = []
            boxes, scores = detector_utils.detect_objects(
                frame, 
                detection_graph, 
                sess)
            # draw bounding boxes
            detector_utils.draw_box_on_image(
                cap_params['num_hands_detect'], 
                cap_params["score_thresh"], 
                scores, boxes, 
                cap_params['im_width'], 
                cap_params['im_height'], 
                frame, 
                midpoint_list)
            # add frame annotated with bounding box to queue
            output_q.put(frame)
            print('Midpoint List', midpoint_list)
            midpoint_q.put(midpoint_list)
            print('Midpoint_Queue', midpoint_q)
            frame_processed += 1
        else:
            output_q.put(frame)
    sess.close()



def send_message(style, delta_x, delta_y):
    body = {}
    body['type'] = 'move'
    if style == "rotate":    
        body['style'] = style
        body['x'] = delta_x
        body['y'] = delta_y
    if style == "translate": 
        pass
    if style == "zoom":
        pass
    print(body)
    conn.sendall(bytes(json.dumps(body) + '\n', 'utf-8'))


def default_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-src',
        '--source',
        dest='video_source',
        type=int,
        default=0,
        help='Device index of the camera.')
    parser.add_argument(
        '-nhands',
        '--num_hands',
        dest='num_hands',
        type=int,
        default=2,
        help='Max number of hands to detect.')
    parser.add_argument(
        '-fps',
        '--fps',
        dest='fps',
        type=int,
        default=1,
        help='Show FPS on detection/display visualization')
    parser.add_argument(
        '-wd',
        '--width',
        dest='width',
        type=int,
        default=300,
        help='Width of the frames in the video stream.')
    parser.add_argument(
        '-ht',
        '--height',
        dest='height',
        type=int,
        default=200,
        help='Height of the frames in the video stream.')
    parser.add_argument(
        '-ds',
        '--display',
        dest='display',
        type=int,
        default=1,
        help='Display the detected images using OpenCV. This reduces FPS')
    parser.add_argument(
        '-num-w',
        '--num-workers',
        dest='num_workers',
        type=int,
        default=4,
        help='Number of workers.')
    parser.add_argument('-q-size',
        '--queue-size',
        dest='queue_size',
        type=int,
        default=5,
        help='Size of the queue.')
    return parser.parse_args()

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    num_frames = 0
    fps = 0
    frame_index = 0

    args = default_args()

    input_q = Queue(maxsize=args.queue_size)
    output_q = Queue(maxsize=args.queue_size)
    midpoint_q = Queue(maxsize=args.queue_size)

    video_capture = WebcamVideoStream(src=args.video_source, width=args.width, height=args.height).start()

    frame_processed = 0
    cap_params = {}
    cap_params['im_width'], cap_params['im_height'] = video_capture.size()
    cap_params['score_thresh'] = score_thresh
    cap_params['num_hands_detect'] = args.num_hands

    # spin up workers to paralleize detection.
    pool = Pool(args.num_workers, worker, (input_q, output_q, midpoint_q, cap_params, frame_processed))

    cv2.namedWindow('Multi-Threaded Detection', cv2.WINDOW_NORMAL)

    with socket.socket() as s: 
        s.bind((HOST, PORT))
        print('Waiting for connection on Host: %s, Port: %s'%(HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        with conn: 
            print('Connected by: ', addr)
            while True:
                frame = video_capture.read()
                frame = cv2.flip(frame, 1)
                frame_index += 1

                input_q.put(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                output_frame = output_q.get()
                output_frame = cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR)

                elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
                num_frames += 1
                fps = num_frames / elapsed_time
                print("frame",  frame_index, num_frames, elapsed_time, fps)

                # Determine Gesture
                midpoint_data = midpoint_q.get()
                if len(midpoint_data): 
                    delta_x = 0
                    delta_y = 0
                    if prev_x != 0 and prev_y != 0: 
                        delta_x = midpoint_data[0][0] - prev_x
                        delta_y = midpoint_data[0][1] - prev_y
                        if abs(delta_x) < delta_thresh and abs(delta_y) < delta_thresh:
                            send_message('rotate', delta_x, delta_y)
                    prev_x = midpoint_data[0][0]
                    prev_y = midpoint_data[0][1]
                
                # Display
                if output_frame is not None:
                    if args.display > 0:
                        if args.fps > 0:
                            detector_utils.draw_fps_on_image("FPS : " + str(int(fps)), output_frame)
                        cv2.imshow('Multi-Threaded Detection', output_frame)

                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    else:
                        if (num_frames == 400):
                            num_frames = 0
                            start_time = datetime.datetime.now()
                        else:
                            print("frames processed: ", frame_index, "elapsed time: ", elapsed_time, "fps: ", str(int(fps)))

    elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
    fps = num_frames / elapsed_time
    print("fps", fps)
    pool.terminate()
    video_capture.stop()
    cv2.destroyAllWindows()
