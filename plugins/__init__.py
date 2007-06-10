modname = {
    'www.duyidu.com':'duyidu',
    'www.readnovel.com':'readnovel',
}
def get_mod(domain):
    return modname.get(domain, None)