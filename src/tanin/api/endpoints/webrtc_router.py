from fastapi import APIRouter


router = APIRouter(
    prefix="/webrtc"
)


@router.get("/config")
async def get_webrtc_config():
    stun_servers = [
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
    ]
    return {"iceServers": stun_servers}