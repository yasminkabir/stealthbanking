import 'dart:convert';
import 'package:http/http.dart' as http;

class ChatService {
  ChatService({
    http.Client? client,
    String? baseUrl,
  })  : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? const String.fromEnvironment(
          'VOC_BACKEND_URL',
          defaultValue: 'http://127.0.0.1:8000',
        );

  final http.Client _client;
  final String _baseUrl;

  Uri _buildChatUri() => Uri.parse('$_baseUrl/chat');

  Future<String> sendMessage(String message) async {
    try {
      final response = await _client.post(
        _buildChatUri(),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'message': message,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to get chat response: ${response.statusCode}');
      }

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return data['response'] as String;
    } catch (e) {
      throw Exception('Chat error: $e');
    }
  }
}


