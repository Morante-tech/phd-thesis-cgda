---
output: pdf_document
---
# Connected images

##About
Algorithms to connect movements between images. We are currently developing two concepts at the same time. One is a standard feedforward fully connected artificial neural network. The other is a own motion network. We compare actual images or images variations (until we decide which method is the best).


### Organization
* In `cross-validation` folder you can find all the data related to the experiments.

* In `synthetic` folder there are several videos to be used during development as examples of synthetic video files.

* In `src` folder you can find the source code, both python and c++ versions.

* In `video-execution` folder you can find some videos showing the execution of the code.


### Formulae

Motion Networks:

The general equation governing the creation of weights between pixels is:

$$
P = \alpha V_{1_{(i,j)}} V_2 - \beta \left|V_2 -  V_{1_{(i,j)}} \right|
$$

$$
W_{pq}  = Clip[P,{0,1}]
$$

Where:

* $\alpha$ is the learning rate.

* $\beta$ is a decay or substraction multplier.

* $V_{1_{(i,j)}}$ is the pixel $(i,j)$ of the variation image 1. The variation image is the absolute 
difference between an image and its previous frame.

* $V2$ is the variation image 2.

* $W_{pq}$ is a submatrix or block of $W$ (the weights matrix). The ranges of the block are: $p=[i * N_2, i * N_2+N]$ and $q=[j * M_2, i * M_2+M]$, where $N_2$ and $M_2$ are the number of rows and columns of $V_2$ respectively.

Simultaneously to this calculation, another matrix is created:

$$
W_t= \sum_{i=1}^{N} \sum_{j=1}^{M}  W_{pq}
$$

There are two possibilities for prediction

* Predict actual image: that is predict image 2 ($F_{2_{pred}}$) having image 1 ($F_1$) and the weights matrix

$$
T = \sum_{i=1}^{N} \sum_{j=1}^{M} \frac{ V_{1_{(i,j)}} W_{pq} }{W_t} 
$$

$$
F_{2_{pred}} = Clip[T,{0,255}]
$$

* Predict variation image: that is predict variation image 2 ($V_{2_{pred}}$) having variation image 1 ($V_1$) and the weights matrix

$$
T = \sum_{i=1}^{N} \sum_{j=1}^{M} \frac{ 255 * V_{1_{(i,j)}} W_{pq} }{W_t} 
$$

$$
V_{2_{pred}} = Clip[T,{0,255}]
$$

## Performance 
The best performance, in quality, currently corresponds to: python neural network.

