from blockchainProg import Node, calculate_hash
import time

# создаем узлы
node1 = Node("Node_1")
node2 = Node("Node_2")
node3 = Node("Node_3")

# добавляем соседей
node1.add_peer(node2)
node1.add_peer(node3)

node2.add_peer(node1)
node2.add_peer(node3)

node3.add_peer(node1)
node3.add_peer(node2)

# установка сложности
difficulty = 5
node1.blockchain.difficulty = difficulty
node2.blockchain.difficulty = difficulty
node3.blockchain.difficulty = difficulty

# создание блоков с индексом 1
block1 = node1.blockchain.create_block('Транзакция A', node1.node_id)
block2 = node2.blockchain.create_block('Транзакция B', node2.node_id)

# майнинг
block1.mine_block(difficulty)
block2.mine_block(difficulty)

# практически одновременная рассылка
node1.broadcast_block(block1)
node2.broadcast_block(block2)

# проверка того, что был принят block1, а не block2
print('\n' + node1.blockchain.chain[-1].data)
print(node2.blockchain.chain[-1].data)
print(node3.blockchain.chain[-1].data+'\n')

# подделка данных в блоке
block = node1.blockchain.chain[-1]
print(f"Исходный блок: {[node1.blockchain.chain[-1].__getattribute__(i) for i in vars(node1.blockchain.chain[-1])]}")
node1.blockchain.chain[-1].data='Транзакция ААА!!!'
node1.blockchain.chain[-1].hash = calculate_hash(node1.blockchain.chain[-1].index,
                                                 node1.blockchain.chain[-1].timestamp,
                                                 node1.blockchain.chain[-1].data,
                                                 node1.blockchain.chain[-1].previous_hash,
                                                 node1.blockchain.chain[-1].nonce)

# вывод измененного блока и проверка валидности
print(f"Измененный блок: {[node1.blockchain.chain[-1].__getattribute__(i) for i in vars(node1.blockchain.chain[-1])]}")
print(f"Целостность цепочки: {node1.blockchain.is_valid()}")
print(f"Валидность блока: {node1.blockchain.is_block_valid(node1.blockchain.chain[-1])}"+'\n')

# новый блок (чтобы цепочка длиннее была)
node1.create_and_broadcast('Транзакция С')

# "перемайнинг"
index = 1 # индекс измененного блока
chain = node1.blockchain.chain
difficulty = node1.blockchain.difficulty
total_time = 0
attempts = 0

for i in range(index, len(chain)):
    block = chain[i]
    block.nonce = 0 # сброс nonce

    if i != 0: # если не генезис-блок, изменяем previous_hash блока
        block.previous_hash = chain[i-1].hash

    start = time.time() # начало майнинга блока
    block.mine_block(difficulty)
    end = time.time() # конец майнинга блока

    total_time += end - start
    attempts += block.nonce # nonce соответствует количеству попыток поиска хэша, который соответствует difficulty

print('\n'+f"Среднее время пересчета хэша: {total_time/attempts}")
print(f"Среднее время на перемайнинг блока: {total_time/(len(chain) - index)}")
print(f"Общее время перемайнинга цепочки: {total_time}")