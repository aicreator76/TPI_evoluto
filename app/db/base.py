from sqlalchemy.ext.declarative import declarative_base

# Base centralizzata per tutti i modelli SQLAlchemy del progetto TPI_evoluto.
# Tutte le tabelle dovranno ereditare da Base.
Base = declarative_base()
