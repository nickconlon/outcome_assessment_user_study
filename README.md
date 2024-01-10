# Outcome Assessment Evaluation

This project is for a human subject study to evaluate the Outcome Assessment algorithm. We investigated how knowledge of robot competency impacts human decision-making when there is uncertainty about the state of the world and the robot's capabilities.

The Outcome Assessment metric from Factorized Machine Self-Confidence enables an autonamous robot to understand its task competency. This project extends the following:

[Machine Self-confidence in Autonomous Systems via Meta-analysis of Decision Processes](https://link.springer.com/chapter/10.1007/978-3-030-20454-9_21)

[Algorithmic Assurances and Self-Assessment of Competency Boundaries in Autonomous Systems](https://www.proquest.com/openview/98e816c88e706dd10df214afe28466e6/1?pq-origsite=gscholar&cbl=18750&diss=y)

We published these papers:

[“I'm Confident This Will End Poorly”: Robot Proficiency Self-Assessment in Human-Robot Teaming](https://ieeexplore.ieee.org/document/9981653)

[Investigating the Effects of Robot Proficiency Self-Assessment on Trust and Performance](https://arxiv.org/abs/2203.10407)


### Installation
Python: 3.8.10

Ubuntu: 20.04

### Usage
This is a Python Flask application. First setup environment variables:
```commandline
$ export FLASK_APP=flaskr
$ export FLASK_ENV=development
```
Start it like any flask app:
```
$ flask init-db
$ flask run
```
