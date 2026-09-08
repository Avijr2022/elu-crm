/// API base URL — override via `--dart-define=API_BASE_URL=http://host:port`.
class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );
}
