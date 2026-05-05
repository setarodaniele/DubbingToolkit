# Scripts/SilenziaWarning.py

import warnings


# Filtra warning già presenti
warnings.filterwarnings("ignore", message="`resume_download` is deprecated", category=FutureWarning)
warnings.filterwarnings("ignore", message="TypedStorage is deprecated", category=UserWarning)


# Nuovi warning visti durante traduzione
warnings.filterwarnings("ignore", message=".*UntypedStorage.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*You are using.*", category=UserWarning)