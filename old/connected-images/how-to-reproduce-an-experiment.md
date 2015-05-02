## How to reproduce an experiment

These are the instructions to reproduce any experiment shown in video execution and others.

1. In order to reproduce a experiment, you need to know wheter it was performed using our `motion` network, or a feedforward neural network (coded as `nn`). This is easy to know, assuming you have the parameters file (you can find many in `./cross-validation/experiments/params` folder). Each parameters file is coded as `NETWORK_params_DATE_TIME.csv`, where `NETWORK` corresponds to `motion` or `nn`.

2. Once you know the type of network, go to ``./src/python/`` and locate `motion` or `nn`.

3. Launch the file you selected (on a terminal) using as argument the parameters file. For example:

    ```
    $ python motion.py  ../../cross-validation/experiments/params/motion_params_20.Mar.2015_03:26:26.csv
    ```

4. As long as the weights file is still available in `./cross-validation/experiments/weights` folder, the program should work. The weights file will have the same DATE and TIME than the parameters file. That's all.

5. **BONUS**: To reproduce plots and analyses, go to `./cross-validation/experiments/scripts` folder. In this folder there are several Rmd (R markdown) and python files, each one performing a different analysis. Each file is intended to be autoexplicative, and can be opened with any text editor.


