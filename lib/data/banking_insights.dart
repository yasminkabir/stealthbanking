import 'dart:convert';

/// Core domain model for the synthetic banking insights payload that powers
/// the graphs and lists in the Flutter demo.
class BankingInsights {
  BankingInsights({
    required this.generatedAt,
    required this.productDemand,
    required this.topRequests,
  });

  final DateTime generatedAt;
  final ProductDemand productDemand;
  final List<String> topRequests;

  factory BankingInsights.fromJson(Map<String, dynamic> json) {
    return BankingInsights(
      generatedAt: DateTime.parse(json['generated_at'] as String),
      productDemand: ProductDemand.fromJson(
        json['product_demand'] as Map<String, dynamic>,
      ),
      topRequests: List<String>.from(json['top_requests_list'] as List<dynamic>),
    );
  }

  static BankingInsights decode(String body) =>
      BankingInsights.fromJson(jsonDecode(body) as Map<String, dynamic>);
}

class ProductDemand {
  ProductDemand({
    required this.topRequestedProducts,
    required this.topRecentImprovements,
    required this.trendWeeks,
  });

  final List<RequestedProduct> topRequestedProducts;
  final List<RecentImprovement> topRecentImprovements;
  final List<TrendWeek> trendWeeks;

  factory ProductDemand.fromJson(Map<String, dynamic> json) {
    return ProductDemand(
      topRequestedProducts: (json['top_requested_products'] as List<dynamic>)
          .map((e) => RequestedProduct.fromJson(e as Map<String, dynamic>))
          .toList(),
      topRecentImprovements: (json['top_recent_improvements'] as List<dynamic>)
          .map((e) => RecentImprovement.fromJson(e as Map<String, dynamic>))
          .toList(),
      trendWeeks: (json['trend_weeks'] as List<dynamic>)
          .map((e) => TrendWeek.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  /// Builds up to [maxSeries] trend series ordered by their latest value.
  List<TrendSeries> buildTrendSeries({int maxSeries = 3}) {
    if (trendWeeks.isEmpty) {
      return const [];
    }
    final labels = <String>{};
    for (final week in trendWeeks) {
      labels.addAll(week.series.keys);
    }
    final series = labels.map((label) {
      final points = trendWeeks
          .map(
            (week) => TrendPoint(
              week: week.week,
              value: week.series[label] ?? 0,
            ),
          )
          .toList();
      return TrendSeries(label: label, points: points);
    }).toList();

    series.sort(
      (a, b) => b.points.last.value.compareTo(a.points.last.value),
    );

    if (series.length > maxSeries) {
      return series.take(maxSeries).toList();
    }
    return series;
  }
}

class RequestedProduct {
  RequestedProduct({
    required this.product,
    required this.featureTag,
    required this.mentions,
    required this.wowChange,
    required this.averageSentiment,
  });

  final String product;
  final String featureTag;
  final int mentions;
  final double wowChange;
  final double averageSentiment;

  factory RequestedProduct.fromJson(Map<String, dynamic> json) {
    return RequestedProduct(
      product: json['product'] as String,
      featureTag: json['feature_tag'] as String,
      mentions: (json['mentions'] as num).toInt(),
      wowChange: (json['wow_change'] as num).toDouble(),
      averageSentiment: (json['average_sentiment'] as num).toDouble(),
    );
  }
}

class RecentImprovement {
  RecentImprovement({
    required this.product,
    required this.bank,
    required this.mentions,
    required this.wowChange,
    required this.averageSentiment,
  });

  final String product;
  final String bank;
  final int mentions;
  final double wowChange;
  final double averageSentiment;

  factory RecentImprovement.fromJson(Map<String, dynamic> json) {
    return RecentImprovement(
      product: json['product'] as String,
      bank: json['bank'] as String,
      mentions: (json['mentions'] as num).toInt(),
      wowChange: (json['wow_change'] as num).toDouble(),
      averageSentiment: (json['average_sentiment'] as num).toDouble(),
    );
  }
}

class TrendWeek {
  TrendWeek({
    required this.week,
    required this.series,
  });

  final DateTime week;
  final Map<String, int> series;

  factory TrendWeek.fromJson(Map<String, dynamic> json) {
    final map = <String, int>{};
    for (final entry in json.entries) {
      if (entry.key == 'week') continue;
      map[entry.key] = (entry.value as num).toInt();
    }
    return TrendWeek(
      week: DateTime.parse(json['week'] as String),
      series: map,
    );
  }
}

class TrendSeries {
  TrendSeries({
    required this.label,
    required this.points,
  });

  final String label;
  final List<TrendPoint> points;
}

class TrendPoint {
  TrendPoint({
    required this.week,
    required this.value,
  });

  final DateTime week;
  final int value;
}

/// Data model for Athena query results
class AthenaQueryResult {
  AthenaQueryResult({
    required this.predictedLabel,
    required this.countPosts,
    required this.avgEngagement,
    required this.weightedPopularity,
  });

  final String predictedLabel;
  final int countPosts;
  final double avgEngagement;
  final double weightedPopularity;
}

