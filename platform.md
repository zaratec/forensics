---
layout: default
---

# Platform

The project uses Docker as an environment to generate the challenge file. This
make the challenge generation portable across operating systems. 

# Setup Instructions

1. **Install Docker:** [Instructions 
to download and set up Docker can be found here](https://docs.docker.com/v17.12/install/).
2. **Build the Docker image:** Run `docker build . -t forensic`
3. **Access the Docker container:** Run `docker run --privileged -it -v $(pwd):/forensics forensics`. 
This will mount the current directory to `/forensics` in the Docker container.
4. **Run the generator script:** Run `python /forensics/generator.py`. This will generate a challenge image `/forensics/hdd.img` and accompanying challenge info `/forensics/flags.txt`.
