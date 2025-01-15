import pika

credentials = pika.PlainCredentials("guest", "custompassword123")
con_str = "amqp://guest:custompassword123@127.0.0.1:5672/"
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="127.0.0.1", port="5672", virtual_host="/", credentials=credentials
    )
)
channel = connection.channel()

channel.queue_declare(queue="hello")

channel.basic_publish(exchange="", routing_key="hello", body="Hello World!")
print(" [x] Sent 'Hello World!'")
connection.close()
