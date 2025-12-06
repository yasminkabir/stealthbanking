import 'dart:io';

import 'package:http/http.dart' as http;

import 'banking_insights.dart';

/// Simple repository for fetching the synthetic banking insights payload.
class InsightsRepository {
  InsightsRepository({
    http.Client? client,
    String? baseUrl,
  })  : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? const String.fromEnvironment(
          'VOC_BACKEND_URL',
          defaultValue: 'http://127.0.0.1:8000',
        );

  final http.Client _client;
  final String _baseUrl;

  Uri _buildUri() => Uri.parse('$_baseUrl/llm/banking-insights');

  Future<BankingInsights> fetchInsights() async {
    try {
      final response = await _client.get(_buildUri());
      if (response.statusCode != HttpStatus.ok) {
        throw HttpException(
          'Unexpected status: ${response.statusCode}',
          uri: _buildUri(),
        );
      }
      return BankingInsights.decode(response.body);
    } on SocketException catch (err) {
      throw HttpException('Failed to reach backend: $err', uri: _buildUri());
    }
  }
}

