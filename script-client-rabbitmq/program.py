import pika

credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.100.29', 5672, '/', credentials))
channel = connection.channel()

def message_received_callback(ch, method, properties, body):
    print("Received body ", body)

channel.basic_consume('comenzi', message_received_callback, auto_ack=True)

print('Astept comenzi...')

channel.start_consuming()


