/// Local API endpoint for host-run FastAPI.
class ApiConfig {
  // Use a completely relative mapping to drop domain lookups entirely
  static const String baseUrl = 'http://127.0.0.1:8000';
}
