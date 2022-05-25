<h1>Virtual ecosystem using NEAT algorism</h1>
Author: Àlex Aspa Garcia
<h2>Introduciton</h2>
The aim of this work was the creation of an intelligent ecosystem where different creatures must learn through evolution to survive in it automatically. The creatures will evolve their neural networks, which we could say is their brain, according to their experiences in this virtual environment. By evaluating their success in each simulation, evolution will form creatures that are more capable of surviving, since they will have learned more rules and situations of the scenario.

This creation has made it possible to explore and work with the NEAT algorithm that aims to evolve the topologies of artificial neural networks from a minimal structure. The evolution of NN is made with a genetic algorithm which will select the best combinations of neural network to generate a better one. In other words, NEAT is an algorithm that evolves neural networks with a genetic algorithm.

Apart from the research, the aim of the work is to create a 0-player game that allows to see the evolution of the creatures in a virtual ecosystem in an infinite way, in order to see how evolution affects them and if we can establish a real simile with the evolution as we know it.

<h2>Code</h2>

Firstly, we read the NEAT configuration file and save all the information in one variable. Also, we will initialize the game by creating the screen and the clock.

Once the scenario has been initialized, a Thread is created for each type of creature which will have to control the population created in each generation of their type of creature. These threads will run indefinitely until the maximum number of evolutions defined or if a creature reaches the marked fitness. In order to coordinate them, it was necessary to implement a system of semaphores in order to respect the update and actions properly.

Network inputs are obtained according to the events that take place on the screen, so it is necessary to coordinate how the scenario is painted so that the data is realistic. The screen update process is as follows; the first of the threads has the permission of the traffic light to act and what it does is update the values ​​of its creatures according to what the other thread has painted on the previous turn and the outputs that the neural network provides, once it has the new calculated positions and states, clear the contents of the screen, and repaint the stage with the new calculated values.

After the update, this thread releases the semaphore and the other thread does the same process, but updating the values of its creatures. 

When the population of that creature is equal to 0, a new generation is re-created using the NEAT-Python library.

Each creature has a class created with different attributes and functions, in order to give some personalization to each of them.

<h2>Files</h2>
<ul>
  <li><strong>config-feedforward</strong>:Configuration file Creature 1</li>
  <li><strong>config-feedforward-2</strong>:Configuration file Creature 2</li>
  <li><strong>recover.py</strong>:This file is used to test the checkpoints created.</li>
  <li><strong>Test.py</strong>:This file is used to train the blue creature in a completely static scenario.</li>
  <li><strong>Test2.py</strong>:This file is used to test and observe the behavior of blue creature trained previously in file: Test.py.</li>
  <li><strong>Tr_blue.py</strong>:This file is used to train the blue creature in different random scenarios.</li>
  <li><strong>Tr_Red.py</strong>:This file is used to train the red creature in different random scenarios.</li>
  <li><strong>Trained.py</strong>:This file is used to test and observe the behavior of 2 already trained creatures.</li>
  <li><strong>Training.py</strong>:This file is used to train both creatures in different random scenarios.</li>
</ul>


