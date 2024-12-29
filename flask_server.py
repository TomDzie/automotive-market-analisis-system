from flask import Flask, jsonify, request
from threading import Lock

app = Flask(__name__)

# Inicjalizacja pięciu kolejek jako list
queues = {f'queue{i}': [] for i in range(1, 4)}

# Tworzymy słownik blokad dla każdej kolejki
queue_locks = {f'queue{i}': Lock() for i in range(1, 4)}

@app.route('/queue/<int:queue_id>', methods=['GET', 'POST', 'DELETE'])
def manage_queue(queue_id):
    queue_name = f'queue{queue_id}'
    if queue_name not in queues:
        return jsonify({"error": "Queue not found"}), 404
    
    lock = queue_locks[queue_name]
    
    # Zabezpieczamy operacje blokadą
    with lock:
        if request.method == 'POST':
            data = request.json
            queues[queue_name].append(data)
            return jsonify({"message": "Data added", "data": data}), 201

        elif request.method == 'DELETE':
            if queues[queue_name]:
                removed_data = queues[queue_name].pop(0)
                return jsonify({"message": "Data removed", "data": removed_data}), 200
            else:
                return jsonify({"message": "Queue is empty"}), 204

        # Pobranie aktualnej zawartości kolejki
        return jsonify(queues[queue_name])

if __name__ == '__main__':
    app.run()

#python Gotowe_programy/flask_server.py