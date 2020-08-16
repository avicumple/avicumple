![Python 2.7](https://img.shields.io/badge/Python-2.7-blue.svg)
![Django 1.5](https://img.shields.io/badge/Django-1.5-blue.svg)

# AVICUMPLE (2013) - deprecated
Gestor para **felicitar los cumpleaños de los amigos de Facebook** creando una publicación con:
- `Mensaje de felicitacion`: "Feliz cumpleaños"
- `Foto personalizada`. Se utiliza la foto de perfil del amigo y se aplica un filtro color sepia junto con un mensaje "HAPPY BIRTHDAY"

Esta app se creó como práctica de una asignatura de carrera en el año 2013, por lo que muchas de sus funcionalidades no funcionan debido a que la mayor parte de las APIs externas que se usaban han sido deprecated.

### Capturas de pantalla
En la carpeta "capturas de pantalla" se encuentran algunos ejemplos de la aplicación como:

##### Pantalla principal
<img src="/capturas_de_pantalla/principal_con_amigos.PNG" width="100%">

##### Ejemplo de una felicitacion de cumpleaños a nuestro amigo Julio Iglesias en Facebook con una foto de su perfil personalizada con un color sepia
<img src="/capturas_de_pantalla/ejemplo_publicacion_facebook.PNG" width="30%">

### Motivos para incorporar este código a Github
- **Aprender**. Todos tenemos unos inicios y la mejor forma de ver como hemos mejorado a lo largo del tiempo es mirar hacia atrás de vez en cuando.
- **Sentimientos**. La nostalgia nos invade, y más con fantásticos compañeros de carrera.

### Componentes
- Facebook API. 
  - Leer información del usuario, amigos y foto de perfil.
  - Publicar el mensaje de felicitación + foto de perfil personalizada color sepia. 
- ImageMagick a través de una librería en lenguaje C.
  - El motivo de este componente era integrar a través de un "wrapper" una librería escrita en otro lenguaje de programación.

### A tener en cuenta
Esta aplicación fue creada por unos estudiantes en sus primeros años de carrera, por ello hay ciertos aspectos a tener en cuenta:
- Estabilidad. El propósito de esta aplicación no fue ser desplegada en un entorno de producción por lo que su estabilidad es cuestionable.
- Deprecations. Desde su creación esta aplicación no ha sido evolucionada más por lo que algunos de sus componentes puede que no funcionen como en el momento de su creación.
- Facebook API. 
  - En el año 2013 los permisos como "leer amigos" o "crear publicación" que son los que utiliza esta app podían solicitarse sin ningún problema. A día de hoy, Facebook requiere que si se necesitan esos permisos la app tiene que se revisada por ellos.
  - Por este y otros motivos no se ha actualizado el API de Facebook a la última versión disponible y se ha habilitado el `modo MOCK` de esta app para poder ver y utilizar la interfaz.

### Uso
Hay 2 formas de usar Avicumple:
1. **Docker** (preferida). Más simple y fácil.
2. **En local**. Instalando las librerías necesarias en un pc/servidor y arrancando la app.

#### 1. DOCKER
- Build de la imagen:
`docker build -t avicumple/avicumple .`
- Arrancar la imagen:
  - Por defecto (Facebook API mockeada): `docker run --rm -p 8000:8000 -it avicumple/avicumple` 
  - Custom (aplicación original): `docker run --env MOCK_FACEBOOK_SERVICES=False --rm -p 8000:8000 -it avicumple/avicumple`

#### 2. LOCAL

##### Instalación
Entorno asegurado Python 2.7, Django 1.5, Debian 9.11 (porque la librería escrita en el lenguage C está compilada en este SO)

Se recomienda usar Virtualenv para instalar las librerísa de Python.
```
virtualenv .
./bin/activate
```

Librerías necesarias por `pycurl`:
```
apt-get install -y libssl-dev libcurl4-openssl-dev
```

Librerias necesarias para utilizar el "filtro sepia" con ImageMagick a través de una librería escrita en C:
```
apt-get install -y imagemagick libmagickwand-dev
```

Python requirements:
```
pip install -r www/appcumple/requirements.txt
```

Modificar la ruta absoluta de la BD en el archivo `appcumple/appcumple/settings.py`:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '[RUTA]/django/www/appcumple/appcumple.db', # Or path to database file if using sqlite3.
        [...]
    }
}
```

##### Uso
Como el API de Facebook que usaba esta aplicación ha sido "deprecated" se ha habilitado un mock para estos servicios.

Por ello se puede ejecutar de 2 opciones:
1. Usar la aplicación con mocks (modo por defecto):
`MOCK_FACEBOOK_SERVICES=True python manage.py runserver` o `python manage.py runserver` 
2. Usar la aplicación original:
`MOCK_FACEBOOK_SERVICES=False python manage.py runserver`


### Compilar y crear Wrapper de la libreria que aplica el "filtro sepia"
Instalar
```
sudo apt-get install libmagickwand-dev imagemagick
sudo apt-get install swig
```

Compilar y Wrapper
```
sudo ln -s /usr/include/x86_64-linux-gnu/ImageMagick-6/magick/magick-baseconfig.h /usr/include/ImageMagick-6/magick/magick-baseconfig.h

gcc -fPIC -lMagickWand -lMagickCore -I /usr/include/ImageMagick-6/  -c filtro.c filtro_wrap.c -I /usr/include/python2.7/

gcc -shared filtro.o filtro_wrap.o -lMagickWand-6.Q16 -lMagickCore-6.Q16 -I /usr/include/ImageMagick-6/ -L /usr/lib/x86_64-linux-gnu/ -Xlinker -rpath /usr/lib -o _filtro.so

swig -python filtro.i
```
