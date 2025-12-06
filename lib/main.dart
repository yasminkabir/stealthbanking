import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'data/banking_insights.dart';
import 'data/chat_service.dart';

void main() {
  runApp(const VocApp());
}

class VocApp extends StatelessWidget {
  const VocApp({super.key});

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xFF2E3A8C); // deep indigo/blue
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Voice of the Customer',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: seed),
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF4F6FB),
      ),
      home: const _Shell(),
    );
  }
}

class _Shell extends StatefulWidget {
  const _Shell();

  @override
  State<_Shell> createState() => _ShellState();
}

class _ShellState extends State<_Shell> {
  int _index = 0;

  final _pages = const [
    HomePage(),
    ChatPage(),
    ResultsPage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.chat_bubble_outline), selectedIcon: Icon(Icons.chat_bubble), label: 'Chat'),
          NavigationDestination(icon: Icon(Icons.format_list_numbered), selectedIcon: Icon(Icons.format_list_numbered), label: 'Insights'),
        ],
      ),
    );
  }
}

/// ------------------------------
/// HOME (Welcome page with navigation instructions)
/// ------------------------------
class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
        children: [
          const SizedBox(height: 24),
          // Logo bars
          SizedBox(
            height: 64,
            child: Center(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  _bar(height: 22, color: cs.primary.withAlpha((255 * .4).round())),
                  const SizedBox(width: 6),
                  _bar(height: 34, color: cs.primary.withAlpha((255 * .6).round())),
                  const SizedBox(width: 6),
                  _bar(height: 52, color: cs.primary),
                ],
              ),
            ),
          ),
          const SizedBox(height: 28),
          Text(
            'VOICE OF THE CUSTOMER',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: cs.primary,
              fontWeight: FontWeight.w800,
              fontSize: 28,
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 32),
          Text(
            'Welcome!',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: cs.onSurface,
              fontWeight: FontWeight.w600,
              fontSize: 24,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Explore banking insights powered by real customer feedback and discussions.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: cs.onSurfaceVariant,
              fontSize: 16,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 40),
          // Navigation Instructions
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: const [
                BoxShadow(blurRadius: 6, color: Color(0x11000000), offset: Offset(0, 2))
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'How to Navigate',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: cs.primary,
                  ),
                ),
                const SizedBox(height: 24),
                _NavigationItem(
                  icon: Icons.chat_bubble_outline,
                  iconColor: cs.primary,
                  title: 'Chat',
                  description: 'Ask questions about banking insights and get answers based on real customer discussions.',
                ),
                const SizedBox(height: 20),
                _NavigationItem(
                  icon: Icons.format_list_numbered,
                  iconColor: cs.primary,
                  title: 'Insights',
                  description: 'View the top 5 banking topics with detailed analytics and visualizations.',
                ),
                const SizedBox(height: 20),
                _NavigationItem(
                  icon: Icons.home_outlined,
                  iconColor: cs.primary,
                  title: 'Home',
                  description: 'Return to this welcome page anytime to see navigation instructions.',
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),
          // Tip section
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: cs.primaryContainer.withOpacity(0.3),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.lightbulb_outline, color: cs.primary, size: 24),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Use the bottom navigation bar to switch between pages. Start by exploring the Chat page to ask questions about banking insights!',
                    style: TextStyle(
                      color: cs.onSurface,
                      fontSize: 14,
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _bar({required double height, required Color color}) {
    return Container(
      width: 18,
      height: height,
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(4),
      ),
    );
  }
}

class _NavigationItem extends StatelessWidget {
  const _NavigationItem({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.description,
  });

  final IconData icon;
  final Color iconColor;
  final String title;
  final String description;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: iconColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: iconColor, size: 24),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: TextStyle(
                  fontSize: 14,
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                  height: 1.4,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// ------------------------------
/// CHAT (functional chatbot with OpenAI and vector search)
/// ------------------------------
class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final _chatService = ChatService();
  final _textController = TextEditingController();
  final _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    // Add initial greeting message
    _messages.add(ChatMessage(
      text: "Hi! What would you like to explore about the current online insights revolving around banking?",
      isUser: false,
    ));
  }

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _sendMessage() async {
    final text = _textController.text.trim();
    if (text.isEmpty || _isLoading) return;

    // Add user message
    setState(() {
      _messages.add(ChatMessage(text: text, isUser: true));
      _textController.clear();
      _isLoading = true;
    });

    // Scroll to bottom
    _scrollToBottom();

    try {
      // Get response from backend
      final response = await _chatService.sendMessage(text);

      setState(() {
        _messages.add(ChatMessage(text: response, isUser: false));
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          text: "Sorry, I encountered an error. Please try again.",
          isUser: false,
        ));
        _isLoading = false;
      });
    }

    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return SafeArea(
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Row(
              children: [
                Expanded(
                  child: Text('VOICE OF THE CUSTOMER',
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 18,
                        color: cs.primary,
                      ),
                      overflow: TextOverflow.ellipsis),
                ),
                const SizedBox(width: 8),
                Icon(Icons.bar_chart, color: cs.primary),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Container(
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Color(0xFFEFF2FB),
                      Colors.white,
                    ],
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length + (_isLoading ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == _messages.length) {
                        // Loading indicator
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          child: Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: cs.surfaceContainerHighest,
                                  borderRadius: BorderRadius.circular(16),
                                ),
                                child: const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                ),
                              ),
                            ],
                          ),
                        );
                      }
                      return _ChatBubble(message: _messages[index], colorScheme: cs);
                    },
                  ),
                ),
              ),
            ),
          ),
          // Input field
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    enabled: !_isLoading,
                    decoration: InputDecoration(
                      hintText: 'Ask about banking insights...',
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: BorderSide(color: cs.outlineVariant),
                      ),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filledTonal(
                  onPressed: _isLoading ? null : _sendMessage,
                  icon: const Icon(Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class ChatMessage {
  final String text;
  final bool isUser;

  ChatMessage({required this.text, required this.isUser});
}

class _ChatBubble extends StatelessWidget {
  const _ChatBubble({required this.message, required this.colorScheme});

  final ChatMessage message;
  final ColorScheme colorScheme;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: message.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser) ...[
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: colorScheme.primary.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.smart_toy, size: 18, color: colorScheme.primary),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: message.isUser
                    ? colorScheme.primary
                    : colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                message.text,
                style: TextStyle(
                  color: message.isUser
                      ? Colors.white
                      : colorScheme.onSurface,
                  fontSize: 14,
                ),
              ),
            ),
          ),
          if (message.isUser) ...[
            const SizedBox(width: 8),
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: colorScheme.primary.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.person, size: 18, color: colorScheme.primary),
            ),
          ],
        ],
      ),
    );
  }
}

/// ------------------------------
/// INSIGHTS (shows top 5 labels with vertical bar charts)
/// ------------------------------
class ResultsPage extends StatefulWidget {
  const ResultsPage({super.key});

  @override
  State<ResultsPage> createState() => _ResultsPageState();
}

class _ResultsPageState extends State<ResultsPage> {
  bool _isLoading = false;

  // Hard-coded Athena query results
  static final List<AthenaQueryResult> _athenaResults = [
    AthenaQueryResult(
      predictedLabel: 'Fees & Charges',
      countPosts: 29325,
      avgEngagement: 0.5123282144586226,
      weightedPopularity: 15024.024888999109,
    ),
    AthenaQueryResult(
      predictedLabel: 'Credit Card',
      countPosts: 24774,
      avgEngagement: 0.5117872612012244,
      weightedPopularity: 12679.017608999135,
    ),
    AthenaQueryResult(
      predictedLabel: 'Security & Fraud',
      countPosts: 20215,
      avgEngagement: 0.503605529507754,
      weightedPopularity: 10180.385778999245,
    ),
    AthenaQueryResult(
      predictedLabel: 'Online Banking',
      countPosts: 10589,
      avgEngagement: 0.47766030748886745,
      weightedPopularity: 5057.944995999617,
    ),
    AthenaQueryResult(
      predictedLabel: 'ATM Service',
      countPosts: 9417,
      avgEngagement: 0.5092664012954946,
      weightedPopularity: 4795.761700999673,
    ),
  ];

  Future<void> _loadLatestResults() async {
    setState(() {
      _isLoading = true;
    });

    // Simulate loading delay
    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return SafeArea(
      child: ListView(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
            children: [
              Text(
                'VOICE OF THE CUSTOMER',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: cs.primary,
                ),
              ),
              const SizedBox(height: 16),
          // Get Latest Insights Button
          FilledButton(
            onPressed: _isLoading ? null : _loadLatestResults,
            style: FilledButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: _isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : const Text('Get Latest Insights', style: TextStyle(fontSize: 16)),
          ),
          if (_isLoading) ...[
            const SizedBox(height: 16),
            // Loading Progress Bar
              Container(
              padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: const [BoxShadow(blurRadius: 6, color: Color(0x11000000), offset: Offset(0, 2))],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                  const Text(
                    'Loading latest insights...',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 12),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      minHeight: 8,
                      backgroundColor: cs.surfaceContainerHighest,
                      valueColor: AlwaysStoppedAnimation<Color>(cs.primary),
                    ),
                  ),
                ],
              ),
            ),
          ],
          if (!_isLoading) ...[
            const SizedBox(height: 24),
            // Top 5 Labels List
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: const [BoxShadow(blurRadius: 6, color: Color(0x11000000), offset: Offset(0, 2))],
              ),
              child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                  const Text(
                    'Top 5 Banking Insights',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 16),
                  ..._athenaResults.map((item) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        child: Text(
                          item.predictedLabel,
                          style: const TextStyle(fontSize: 16),
                        ),
                      )),
                ],
              ),
            ),
            const SizedBox(height: 24),
            // Weighted Popularity Vertical Bar Chart
            _VerticalBarChart(
              title: 'Weighted Popularity',
              data: _athenaResults,
              getValue: (item) => item.weightedPopularity,
              formatValue: (value) => value.toStringAsFixed(2),
              color: Colors.orange,
            ),
            const SizedBox(height: 24),
            // Count Posts Vertical Bar Chart
            _VerticalBarChart(
              title: 'Count Posts',
              data: _athenaResults,
              getValue: (item) => item.countPosts.toDouble(),
              formatValue: (value) => value.toInt().toString(),
                                  color: cs.primary,
                                ),
            const SizedBox(height: 24),
            // Average Engagement Vertical Bar Chart
            _VerticalBarChart(
              title: 'Average Engagement',
              data: _athenaResults,
              getValue: (item) => item.avgEngagement,
              formatValue: (value) => value.toStringAsFixed(4),
              color: Colors.green,
            ),
          ],
        ],
      ),
    );
  }
}

class _VerticalBarChart extends StatelessWidget {
  const _VerticalBarChart({
    required this.title,
    required this.data,
    required this.getValue,
    required this.formatValue,
    required this.color,
  });

  final String title;
  final List<AthenaQueryResult> data;
  final double Function(AthenaQueryResult) getValue;
  final String Function(double) formatValue;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final maxValue = data.map(getValue).reduce(math.max);
    final chartHeight = 200.0;
    final barWidth = 40.0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [BoxShadow(blurRadius: 6, color: Color(0x11000000), offset: Offset(0, 2))],
      ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
            title,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: cs.primary,
            ),
                                    ),
          const SizedBox(height: 24),
          SizedBox(
            height: chartHeight + 100,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: data.asMap().entries.map((entry) {
                final item = entry.value;
                final value = getValue(item);
                final height = maxValue > 0 ? (value / maxValue) * chartHeight : 0.0;
                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 2),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Flexible(
                          child: Text(
                            formatValue(value),
                                      style: TextStyle(
                              fontSize: 9,
                              fontWeight: FontWeight.w600,
                              color: cs.primary,
                            ),
                            textAlign: TextAlign.center,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Container(
                          width: double.infinity,
                          height: height,
                          decoration: BoxDecoration(
                            color: color,
                            borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
                                      ),
                                    ),
                        const SizedBox(height: 8),
                        Flexible(
                          child: Text(
                            item.predictedLabel,
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontSize: 9),
                            maxLines: 3,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
                ),
              ),
            ],
      ),
    );
  }
}
