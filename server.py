from waitress import serve
import portal

serve(portal.app, host='0.0.0.0', port=8080, threads=8)