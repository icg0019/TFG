class Config: 
  SECRET_KEY ='Aljdm56+dkf6s'

class DevelopmentConfig(Config):
  DEBUG=True
  MYSQL_HOST='FNSVSQL05'
  MYSQL_USER = 'sa'
  MYSQL_PASSWORD = 'FNSVSQL05'
  MYSQL_DB= 'PEDIDOS_TETRA_DB'
   
config={
    'development': DevelopmentConfig
  }
  