from nameko.rpc import rpc

class VolumeService:
    name = "volumes"

    @rpc
    def health(self):
        return {"status": "success"}
    
    @rpc
    def prepare_data(self):
        return "Hello"
