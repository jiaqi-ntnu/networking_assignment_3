from abc import abstractmethod, ABC
import logging
import socket
from multiprocessing.synchronize import Event as EventType
class TransportProtocol(ABC):
    from server_handler import ServerHandler

    def __init__(self, serverHandler:ServerHandler, host:str, port:int ) -> None:
        super().__init__()
        self._serverHandler = serverHandler
        self._addr = host,port


    @abstractmethod
    def startServer(self, serverReadyEvent:EventType):
        pass


    @abstractmethod
    def handleClient(self, conn):
        pass

    
    @abstractmethod
    def close(self):
        pass



class TCPTransport(TransportProtocol):
    def startServer(self, serverReadyEvent:EventType):
        self._ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._ss.bind(self._addr)
            logging.debug(f"ServerHandler: listening on {self._addr}")
            self._ss.listen()
            serverReadyEvent.set()
            conn, addr = self._ss.accept()
            logging.debug(f"ServerHandler: client from {addr} connected ")
            self.handleClient(conn)
        except Exception as e:
            logging.debug(e)
            logging.debug("Terminating")
        finally:
            logging.debug("Terminating Server")
            self.close()


    def handleClient(self, conn):
        while True:
            message = conn.recv(1024)
            if message:
                logging.debug(f"ServerHandler: Received {message} from client")
                conn.sendall(self._serverHandler.processMessage(message))
            else:
                logging.debug(f"ServerHandler: Client disconnected.")
                break

    def close(self):
        self._ss.close()


class UDPTransport(TransportProtocol):
    def startServer(self, serverReadyEvent:EventType):
        self._ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._ss.bind(self._addr)
            serverReadyEvent.set()
            logging.debug(f"ServerHandler: listening on {self._addr}")
            self.handleClient(self._ss)
        except Exception as e:
            logging.debug(e)
            logging.debug("Terminating")
        finally:
            logging.debug("Terminating Server")
            self.close()

    def handleClient(self, conn):
        while True:
            message,addr = conn.recvfrom(1024)
            if message:
                logging.debug(f"ServerHandler: Received {message} from client")
                conn.sendto(self._serverHandler.processMessage(message), addr)
            else:
                logging.debug(f"ServerHandler: Client disconnected.")
                break

    def close(self):
        self._ss.close()