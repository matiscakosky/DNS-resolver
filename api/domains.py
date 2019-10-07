from flask import abort, make_response
import dns.resolver

counter = 0
domains = {}
custom_domains = set()

def obtain_ip(domain):
    """
    Esta funcion maneja el request GET /api/domains/<domain>

    :return:        200 direccion IP asociada a un dominio en particular
    """
    try:
        if not domain in domains:
            dns_results = dns.resolver.query(domain)
            ips = [ip.address for ip in dns_results]
            domains[domain] = {"domain": domain, "ip": ips, "custom": False}
        global counter
        ips = domains[domain]["ip"]
        if domain in custom_domains:
            return {"domain": domain, "ip": ips, "custom": True}
        ip = ips[counter % len(ips)]
        counter += 1
        return {"domain": domain, "ip": ip, "custom": False}
    except:
        return make_response({"error": "domain not found"}, 404)

def create(**kwargs):
    """
    Esta funcion maneja el request POST​ ​/api/custom-domains

     :param body:  custom domain a crear en la lista de domains
    :return:        201 custom domain creado, 400 custom domain duplicado o cuerpo de request mal formado
    """
    custom_domain = kwargs.get('body')
    domain_body = custom_domain.get('domain')
    ip = custom_domain.get('ip')
    if not domain_body or not ip:
        return make_response({"error": "payload is invalid"}, 400)
    for domain in custom_domains:
        if domains[domain]["ip"] == ip:
            return make_response({"error": "custom domain already exists"}, 400)
    
    custom_domains.add(domain_body)
    domains[domain_body] = {"domain": domain_body, "ip": ip, "custom": True}
    return make_response(domains[domain_body], 201)

def edit(**kwargs):
    """
    Esta funcion maneja el request PUT​ ​/api/custom-domains

     :param body:  custom domain a editar en la lista de domains
    :return:        200 custom domain editado, 404 custom domain no existente o 400 por cuerpo de request mal formado
    """
    custom_domain = kwargs.get('body')
    domain_parameter = kwargs.get('domain')
    domain = custom_domain.get('domain')
    ip = custom_domain.get('ip')
    if not domain or not ip or domain_parameter != domain:
        return make_response({"error": "payload is invalid"}, 400)
    if domain not in custom_domains:
        return make_response({"error": "domain not found"}, 404)
    domains[domain] = {"domain": domain, "ip": ip, "custom": True}
    return domains[domain]

def delete(domain): 
    """
    Esta funcion maneja el request DELETE​ /api/custom-domain/<domain>

    :param body:  custom domain que se quiere borrar
    :return:        200 custom domain, 404 custom domain no encontrado
    """
    if domain not in custom_domains:
        return make_response({"error": "domain not found"}, 404)

    del domains[domain]
    custom_domains.remove(domain)

    return {"domain": domain}

def obtain_all(q = None):
    """
    Esta funcion maneja el request GET /api/custom-domains

    :return:        200 lista de todos los custom domains existentes en el sistema 
    """
    response = {"items": []}
    for elem in domains:
        if domains[elem]["custom"] and (q == None or q in elem):
            response["items"].append(domains[elem])
    return response    
