# cintelink-challenge
Sistema de notificaciones instantáneas para usuarios de una plataforma

* Repositorio del websocket
https://github.com/dariomolina/cintelink-challenge

* Repositorio para demo del websocket
https://github.com/dariomolina/citelink-client


### Versiones de docker y docker-compose
Docker version 20.10.18
Docker Compose version v2.19.1

### Arquitectura General
* Django como framework principal debido a su rapidez en el desarrollo, estructura clara, y su potente ORM.
* PostgreSQL como base de datos por su capacidad para manejar datos complejos y realizar consultas avanzadas.
* Redis con Django Channels para manejar notificaciones en tiempo real.

### Arquitectura de servicios
Los servicios que se definen a continuación se interrelacionan para construir una 
arquitectura de aplicación web que maneja tanto tráfico HTTP como WebSocket, soportada por 
una base de datos PostgreSQL y un sistema de caché Redis
* Nginx: actúa como la puerta de entrada a la aplicación, redirigiendo el tráfico HTTP a 
wsgiserver y el tráfico WebSocket a asgiserver.
* wsgiserver y asgiserver manejan la lógica de la aplicación, interactuando con db-citelink 
para operaciones en la base de datos y con redis para manejar datos en caché o sesiones.
* Redis y postgres soportan a los servidores web proporcionando almacenamiento rápido y 
persistente, respectivamente.

### Funcionalidades

#### 1. Persistencia y Acceso a Notificaciones:
* Las notificaciones se almacenan en la base de datos y pueden ser recuperadas en cualquier momento.
* Cada usuario tiene acceso a su propio historial de notificaciones.

#### 2. Marcado de Notificaciones como Leídas/Eliminadas:
* Las notificaciones pueden marcarse como leídas o eliminadas
* Las eliminadas quedan con eliminado lógico

#### 3. Historial de Notificaciones:
* Las notificaciones leídas y no leídas se muestran en el historial.
* Solo listamos las notificaciones no eliminadas.

#### 4. Explicación del Diseño
* Tag: Son etiquetas que se sirve para poder suscripcion de usuarios.
* Notification: Almacena las notificaciones con un mensaje, un timestamp y una etiqueta.
* NotificationSubscription: Relaciona usuarios con etiquetas (tags). Permite suscribirse 
a notificaciones relacionadas con una etiqueta específica.
* UserNotification: Permite a los usuarios marcar las notificaciones como leídas y 
gestionar el estado de las notificaciones. Cada usuario tiene un historial de notificaciones con su estado.

Cuando se crea una Notification, verificamos los tags y los users que tiene suscripto y
creamos los registros de UserNotification que almacena las notificaciones de cada usuario
relacionado a una Notification.
Cuando se crea cada uno de los UserNotification, se envía mediante el socket un mensaje al canal
del usuario que se encuentra conectado con la data de las notificaciones.
Cada notificacion es enviada al usuario que corresponda y segun el tag que tenga subscripto.

#### 6. Real-time Notifications:
Integración de Django Channels con Redis para manejar notificaciones en tiempo real.
Implementación de WebSockets para notificaciones instantáneas.


### Sistema de Audit Logging
Se utilizó la libreria django-auditlog para registrar automáticamente los cambios en las 
notificaciones.
Se genera una tabla en la base de datos llamana LogEntries, con los siguientes campos

* Created: fecha de creación de la acción
* Resource: Qué modelo o tabla se modificó
* Action: Qué acciónes se realizarion (ej, create, update)
* Changes: Informa qué campos se modificaron y la cantidad de cambios (5 changes: id, user, is_read, is_deleted)
* User: El usuario que realizó la acción

### Dockerización
Crea un Dockerfile para empaquetar la aplicación y un docker-compose.yml para orquestar los servicios, 
incluyendo la base de datos y Redis.

### Seguridad y Testing
* Seguridad: Implementación de autenticación JWT para asegurar las rutas de la API.
* Testing: Se generaron tests unitarios para testing de modelos, vistas y serializers 
usando pytest en notificatio/tests.py.

### Websocket
La url para el uso del websocket es:

ws://127.0.0.1:9000/ws/notifications/?token={USER_TOKEN}

Y podemos usar postman para obtener un listado de notificaciones del user 
* lista de notificaciones
{"type": "notifications_list", "page": 1, "page_size": 5}


### Endpoints

*inicialmente creamos el superuser con el siguiente comando
```
docker-compose -f docker-compose-prod.yml run --rm wsgiserver python manage.py createsuperuser

username: admin
email: d@d.com
pass: admin
```

* Obtener Token (access) para poder realizar requests con los endpoints y el websocket con las 
credenciales de algun usuario registrado (en este caso se usa el usuario admin)
```
POST http://localhost:8000/api/token/
Body
{
    "username": "admin",
    "password": "admin"
}

Response:
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyMzY1MjI3NCwiaWF0IjoxNzIzNTY1ODc0LCJqdGkiOiJiYzk4Y2FmMWE5ODI0MGYzYmFkOGQ0YTMyOGEwY2ZiNSIsInVzZXJfaWQiOjF9.4uz-fnFs_h1eQj02eWyGIVgU3rlhwCy0B7igVhmwmGM",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIzNTY5NDE0LCJpYXQiOjE3MjM1NjU4NzQsImp0aSI6IjY4ZDAyOGQ5MGZiOTQ3YjdiYjE0NTRjNzRlNDIyZGJlIiwidXNlcl9pZCI6MX0._YI6uIqpRElPAaLGAx2_eN3E-9jAyCWq1UOgKB6UNts"
}
```

* Crear un tag: Pasamos  el nombre nombre del tag a crear
```
POST http://localhost:8000/api/tags/
Body:
{
    "name": "deportes"
}

Response:
{
    "id": 1,
    "name": "deportes"
}
```
* Crear una suscripcion: creamos la suscrición con el id del user y el id 
del tag correspondiente
```
POST http://localhost:8000/api/subscriptions/
Body:
{
    "user": 1,
    "tag": 1
}

Response:
{
    "id": 1,
    "user": 1,
    "tag": 1,
}
```


Para probar el websockert, se generó un pequeño front donde lo se lo puede desacargar en 
https://github.com/dariomolina/citelink-client
Buildeamos y levantamos el proyecto de front
```
$ docker-compose build
$ docker-compose up
```


* Debemos obtener el Token (access) para poder realizar conectarnos al websocket mediante el 
uso de la app demo de front con las credenciales de algun usuario registrado (en este caso se usa el usuario admin)
```
POST http://localhost:8000/api/token/
Body
{
    "username": "admin",
    "password": "admin"
}

Response:
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyMzY1MjI3NCwiaWF0IjoxNzIzNTY1ODc0LCJqdGkiOiJiYzk4Y2FmMWE5ODI0MGYzYmFkOGQ0YTMyOGEwY2ZiNSIsInVzZXJfaWQiOjF9.4uz-fnFs_h1eQj02eWyGIVgU3rlhwCy0B7igVhmwmGM",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIzNTY5NDE0LCJpYXQiOjE3MjM1NjU4NzQsImp0aSI6IjY4ZDAyOGQ5MGZiOTQ3YjdiYjE0NTRjNzRlNDIyZGJlIiwidXNlcl9pZCI6MX0._YI6uIqpRElPAaLGAx2_eN3E-9jAyCWq1UOgKB6UNts"
}
```

* con el TOKEN "access", nos dirijimos a la app demo de front citelink-client/ y lo asignamos 
a la variable VITE_WS_TOKEN del archivo .env, ubicado en frontend/.env. Esto es para poder 
conectarse al websocket desde la app demo de front

Luego en htpp://localhost:3000 podemos observar, en el apartado de Notifications, cómo en tiempo real van apareciendo las notificaciones al momento de crear un registro de notificaciones en la db.
En el apartado "All Notifications" se listan todas las notificaciones que tiene el user, teniendo la posibilidad de marcar como leido
y de eliminarlo (eso básicamente marca las notificaciones a nivel base de datos como leida y borrada, pero el borrado es sólo de manera logica, dado que el registro segirá existiendo, pero con el flag is_deleted=True)


Luego de eso, podemos ingresar a postman y crear Notifications.
Este endpoint creará y enviará notificaciones mediante django-channels a todos los users con el tag_id=1 
segun este ejemplo:
```
Estructura del body
{
    "message": <string>,
    "tag": <tag_id> Este registro con el id que se desea enviar, debe existir en la db
}


POST http://localhost:8000/api/notifications/

Body:
{
    "message": "nueva notificacion",
    "tag": 1
}

Response:
{
    "id": 55,
    "tag": 1,
    "message": "nueva notificacion",
    "timestamp": "2024-08-13T14:46:38.346597Z"
}
```
Luego en htpp://localhost:3000 (servicio de front) podemos observar, en el apartado de 
"Notifications", cómo en tiempo real van apareciendo las notificaciones al momento de crear 
un nuevo registro de notificaciones en la db mediante el endpoint [ POST http://localhost:8000/api/notifications/ ]
mensionado anteriormente.

En el apartado "All Notifications" se listan todas las notificaciones que tiene el user, 
teniendo la posibilidad de marcar como leido
y de eliminarlo (eso básicamente marca las notificaciones a nivel base de datos como leida y 
borrada, pero el borrado es sólo de manera logica, dado que el registro segirá existiendo, 
pero con el flag is_deleted=True)



### Bibliografía:
* https://medium.com/@codealfi/building-a-real-time-chat-application-with-django-channels-and-redis-25395a9ffa81
* https://channels.readthedocs.io/en/latest/topics/authentication.html
* https://stackoverflow.com/questions/72775881/django-channels-unable-to-connectfind-websocket-after-docker-compose-of-projec
* https://django-auditlog.readthedocs.io/en/latest/
