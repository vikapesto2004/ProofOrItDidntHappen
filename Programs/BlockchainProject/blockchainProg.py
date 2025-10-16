from datetime import datetime
from hashlib import sha256


def calculate_hash(index, timestamp, data, previous_hash, nonce): # расчет хэша на основе данных блока
    preprocess = (' '.join(str(i) for i in [index, timestamp,
                                            data, previous_hash,
                                            nonce])).encode('utf-8')
    return sha256(preprocess).hexdigest()

def simulate_network_delivery(sender, receiver, block): # добавляет блок в очередь получателя
    receiver.incoming_queue.append(block)
    receiver.process_next_message()


class Block: # класс Block - создание блока
    # инициализация блока с индексом, меткой, данными, пред хэшем и создателем
    def __init__(self, index: int,
                 timestamp: str,
                 data,
                 previous_hash: str,
                 nonce: int,
                 creator="God"):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce # число, выбираемое в процессе майнинга
        self.hash = calculate_hash(self.index, self.timestamp, self.data, self.previous_hash, self.nonce)
        self.creator = creator

    # майнинг блока, нахождение nonce. difficulty - количество нулей в начале хэша
    def mine_block(self, difficulty=4):
        self.nonce = 0
        while True:
            self.hash = calculate_hash(self.index, self.timestamp,
                                       self.data, self.previous_hash,
                                       self.nonce)
            if self.hash.startswith('0' * difficulty):
                return self.hash
            self.nonce += 1




class Blockchain: # класс Blockchain - создание цепочки chain из экземпляров Block
    # инициализация генезис-блока и цепочки chain, добавление генезис-блока в chain
    def __init__(self, difficulty=4):
        self.chain = []
        genesis_block = Block(0, datetime.now().strftime('%d/%m/%Y, %H:%M:%S'),
                              'Neon Genesis Block', '0', 0)
        self.chain.append(genesis_block)
        self.difficulty = difficulty

    #создание блока без добавления в chain
    def create_block(self, data, creator):
        index = len(self.chain)
        timestamp = datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
        previous_hash = self.chain[-1].hash
        new_block = Block(index, timestamp, data, previous_hash, 0, creator)
        return new_block

    # добавление очередного блока в chain (ИЗМЕНЕНО)
    def add_block(self, data, creator):
        index = len(self.chain)
        timestamp = datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
        previous_hash = self.chain[-1].hash
        new_block = Block(index, timestamp, data, previous_hash, 0, creator)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    # добавление очередного блока в chain без проверки
    def add_block_without_validation(self, block):
        self.chain.append(block)

    # проверка целостности chain (ИЗМЕНЕНО)
    def is_valid(self):
        if len(self.chain) == 0:
            return False

        genesis = self.chain[0]

        if genesis.previous_hash != '0' or genesis.index != 0 or \
                calculate_hash(0, genesis.timestamp, genesis.data, '0', 0) != genesis.hash:
            return False

        for i in range(1, len(self.chain)):
            current, previous = self.chain[i], self.chain[i - 1]
            if current.index - previous.index != 1:
                return False

            if current.previous_hash != previous.hash:
                return False

            if not current.hash.startswith('0' * self.difficulty): # ДОБАВЛЕНА ПРОВЕРКА difficulty
                return False

            if calculate_hash(current.index, current.timestamp, current.data,
                              current.previous_hash, current.nonce) != current.hash: # ИЗМЕНЕНА ПРОВЕРКА С УЧЕТОМ nonce
                return False
        return True

    def is_block_valid(self, block):
        # ИЗМЕНЕНА ПРОВЕРКА С УЧЕТОМ nonce
        if block.hash != calculate_hash(block.index, block.timestamp, block.data, block.previous_hash, block.nonce):
            return False

        previous = self.chain[-1]
        if block.previous_hash != previous.hash:
            return False

        if not block.hash.startswith('0' * self.difficulty): # ДОБАВЛЕНА ПРОВЕРКА difficulty
            return False

        return True


class Node: # класс Node - создание узла в P2P-сети
    # инициализация узла с индексом node_id, списка соседей peers, локальной копии блокчейна blockchain
    def __init__(self, node_id):
        self.node_id = node_id
        self.peers = []
        self.blockchain = Blockchain()
        self.incoming_queue=[] # очередь входящих сообщений

    # добавление соседа в список peers
    def add_peer(self, peer_node):
        self.peers.append(peer_node)

    # отправка блока всем узлам в peers
    def broadcast_block(self, block):
        print(f"{self.node_id} рассылает блок '{block.data}'")
        for peer in self.peers:
            if peer.node_id != self.node_id:
                simulate_network_delivery(self.node_id, peer, block)

    # проверка наличия блока с таким индексом в blockchain
    def has_block_at_index(self, index):
        return any(block.index == index for block in self.blockchain.chain)

    # получение и обработка блока
    def receive_block(self, block):
        if any(b.hash == block.hash for b in self.blockchain.chain):
            return False

        if block.index != len(self.blockchain.chain):
            print(f"{self.node_id} отклонил блок '{block.data}': неверный индекс")
            return False

        if self.blockchain.is_block_valid(block):  # проверка хэшей, difficulty и nonce
            # Если блок первый с таким index — принимаем
            if not self.has_block_at_index(block.index):
                self.blockchain.add_block_without_validation(block)  # или напрямую
                self.broadcast_block(block)  # ретрансляция
                print(f"{self.node_id} принял блок '{block.data}' от {block.creator}!")
                return True

        else:
            print(f"{self.node_id} отклонил блок '{block.data}': неверный hash, nonce или difficulty")
            return False


    # обработка сообщения
    def process_next_message(self):
        block = self.incoming_queue.pop(0)  # достаем и удаляем первый блок
        return self.receive_block(block)

    # создание и рассылка блока
    def create_and_broadcast(self, data):
        new_block = self.blockchain.create_block(data, self.node_id)
        new_block.mine_block(self.blockchain.difficulty)
        self.broadcast_block(new_block)



