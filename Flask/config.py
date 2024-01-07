class Config:
  SECRET_KEY ='Aljdm56+dkf6s'

class DevelopmentConfig(Config):
  DEBUG=True


config={
    'development': DevelopmentConfig
  }
  