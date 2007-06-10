from utils import validator as Valid
from apps.zipbooks.models import Book

class AddValidator(Valid.Validator):
    url = Valid.CharField()
    
