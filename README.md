# Molecular Playground Local Python Server

- Adapted from Victor Dibia, Real-time Hand-Detection using Neural Networks (SSD) on Tensorflow, (2017), GitHub repository, https://github.com/victordibia/handtracking


### Notes
---

```(javascript)
predictions: 
[{
bbox: [x, y, width, height],
class: "hand",
score: 0.8380282521247864
}, {
bbox: [x, y, width, height],
class: "hand",
score: 0.74644153267145157
}]

[{…}]
0: {bbox: Array(4), class: 0, score: 0.9765641689300537}
length: 1
__proto__: Array(0)


 console.log("Predictions: ", predictions);
        if (predictions.length > 0) {
            x.innerText = predictions[0].bbox[0].toFixed(2);
            y.innerText = predictions[0].bbox[1].toFixed(2);
        }
```