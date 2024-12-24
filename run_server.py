import argparse
import os
import logging
import sys
import time
from whisper_live.server import TranscriptionServer
from whisper_live.log import LOG_LEVEL, log_levels, CONTAINER


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p',
                        type=int,
                        default=9090,
                        help="Websocket port to run the server on.")
    parser.add_argument('--backend', '-b',
                        type=str,
                        default='faster_whisper',
                        help='Backends from ["tensorrt", "faster_whisper"]')
    parser.add_argument('--faster_whisper_custom_model_path', '-fw',
                        type=str, default=None,
                        help="Custom Faster Whisper Model")
    parser.add_argument('--trt_model_path', '-trt',
                        type=str,
                        default=None,
                        help='Whisper TensorRT model path')
    parser.add_argument('--trt_multilingual', '-m',
                        action="store_true",
                        help='Boolean only for TensorRT model. True if multilingual.')
    parser.add_argument('--omp_num_threads', '-omp',
                        type=int,
                        default=1,
                        help="Number of threads to use for OpenMP")
    parser.add_argument('--no_single_model', '-nsm',
                        action='store_true',
                        help='Set this if every connection should instantiate its own model. Only relevant for custom model, passed using -trt or -fw.')
    
    parser.add_argument('--debug', '-d',
                        choices=log_levels.keys(),
                        default='warning',
                        help="Debug level (debug, info, warning, error, critical)")

    parser.add_argument('--container', '-c',
                        type=int, default=1,
                        help='num of container for log')
    
    parser.add_argument('--max_client', '-mc',
                        type=int, default=4,
                        help='num of maximum client(4)')
    
    parser.add_argument('--max_time', '-mt',
                        type=int, default=600,
                        help='The maximum duration (in seconds) a client can stay connected. Defaults\
     to 600 seconds (10 minutes).')
    
    args = parser.parse_args()
    try:
        if args.backend == "tensorrt":
            if args.trt_model_path is None:
                raise ValueError("Please Provide a valid tensorrt model path")

        if "OMP_NUM_THREADS" not in os.environ:
            os.environ["OMP_NUM_THREADS"] = str(args.omp_num_threads)

        CONTAINER = int(args.container)
        LOG_LEVEL.setLevel(log_levels[args.debug])
        formatter = logging.Formatter(f'%(asctime)s - %(name)s{CONTAINER} - %(levelname)s - %(message)s - %(funcName)s(%(lineno)d)', "%Y-%m-%d %H:%M:%S")
        logging.Formatter.converter = time.localtime
        file_handler = logging.FileHandler(f"/var/log/whisper/whisperLive{args.container}.log")
        file_handler.setFormatter(formatter)
        LOG_LEVEL.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        LOG_LEVEL.addHandler(console_handler)
        server = TranscriptionServer(max_client=int(args.max_client), 
                                    max_connection_time=int(args.max_time))
    except Exception as e:
        LOG_LEVEL.error(f"{e}")
        sys.exit(1)
    
    server.run(
        "0.0.0.0",
        port=args.port,
        backend=args.backend,
        faster_whisper_custom_model_path=args.faster_whisper_custom_model_path,
        whisper_tensorrt_path=args.trt_model_path,
        trt_multilingual=args.trt_multilingual,
        single_model=not args.no_single_model,
    )
