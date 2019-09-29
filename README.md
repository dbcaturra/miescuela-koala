# Miescuela

El proyecto miescuela-koala es un aplicación web que se ejecuta localmente
en su dispositivo android y que le permite gestionar varios procesos de enseñanza
aprendizaje de sus estudiantes en las zonas rurales donde la conectividad a internet
y el suministro de energia electrica presentan constantes limitaciones tales como: 
interrupciones de servicio y baja cobertura.

## Opensource project
Miescuela-koala use koala-lms (https://www.koala-lms.org/) and django_quiz (https://github.com/tomwalker/django_quiz).


## :school: What is Koala LMS?

**Koala LMS** is a **Learning Management System** (*LMS*) that aims to be simple, **made by users**, **for users**. It has been originally developed in the [LORIA Laboratory](http://www.loria.fr/fr/), Nancy, France.

Contrary to other LMS like Moodle for instance, **Koala LMS** wants to stay **simple**, **user focused** and without useless functionalities. Features and requirements come from interviews of people from the [Université de Lorraine](https://www.univ-lorraine.fr/), Nancy, France.

A demonstration instance is available at [demo.koala-lms.org](https://demo.koala-lms.org). It is populated with sample data and refreshed every ten minutes (ie: 2:20; 2:30, etc.). Login as “Erik Orsenna” to access relevant data with the following credentials: `erik-orsenna` and `koala-lms` as the password. Up to now, the demonstration server is populated with data in french, coming from Wikipedia.

**Koala-LMS** components are free software (free as in freedom). All of them are distributed under the [**GPLv3 Licence**](https://www.gnu.org/licenses/quick-guide-gplv3.en.html). We want free code to **remain free**! :blush:

### Technical requirements

**Koala LMS** and the components run with [**Django 2.2**](https://docs.djangoproject.com/en/2.2/releases/2.2/) and [**version 3.7**](https://www.python.org/downloads/release/python-370/). Only **long term support Django releases** will be supported in the future.

## :ship: Start using Docker

You need to [install `docker`](https://docs.docker.com/install/) on your system. We host the [docker image in the Gitlab Registry](https://gitlab.com/koala-lms/lms/container_registry). Its `Dockerfile` is located at [`./docker/stable/Dockerfile`](docker/stable/Dockerfile). You can get the image (*<50MB to download*) using:
```bash
docker pull registry.gitlab.com/koala-lms/lms
```

#### Tweak Docker deployment

You can tweak the `koala-lms` deployment using some environment variables. None is required.
* `LANGUAGE_CODE`: the Django corresponding setting.
* `TIME_ZONE`: the Django corresponding setting.
* `FIXTURE`: the fixture to load (relative to the project directory, ie: `./fixtures/sample.json`)
* `DEMO`: if you wish to enable the demonstration server
* `DEMONSTRATION_LOGIN`: the user that exists in the *fixture* that will be logged in
* `DEBUG`: whether to use Django debug mode.

#### Start the container

To run `miescuela-koala` see INSTALL file.
