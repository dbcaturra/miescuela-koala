ffmpeg -re -i ~/storage/shared/miescuela-koala/static/videos/definiciones.mp4 -c copy -f flv rtmp://0.0.0.0/live/definiciones.mp4
#ffmpeg -re -i ~/storage/shared/miescuela-koala/static/videos/definiciones.mp4 -c:v libx264 -preset superfast -tune zerolatency -c:a aac -ar 44100 -f flv rtmp://0.0.0.0/live/stream
