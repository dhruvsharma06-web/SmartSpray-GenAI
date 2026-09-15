import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../features/dashboard/dashboard_screen.dart';
import '../features/scan/scan_screen.dart';
import '../features/history/history_screen.dart';
import '../features/device/device_screen.dart';
import '../features/zones/zone_details_screen.dart';
import '../features/weather/weather_risk_screen.dart';
import '../widgets/main_scaffold.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();

final router = GoRouter(
  navigatorKey: _rootNavigatorKey,
  initialLocation: '/dashboard',
  routes: [
    StatefulShellRoute.indexedStack(
      builder: (context, state, navigationShell) {
        return MainScaffold(navigationShell: navigationShell);
      },
      branches: [
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/dashboard',
              builder: (context, state) => const DashboardScreen(),
            ),
          ],
        ),
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/scan',
              builder: (context, state) => const ScanScreen(),
            ),
          ],
        ),
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/history',
              builder: (context, state) => const HistoryScreen(),
            ),
          ],
        ),
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/device',
              builder: (context, state) => const DeviceScreen(),
            ),
          ],
        ),
      ],
    ),
    // Sub-routes outside shell navigation bar
    GoRoute(
      path: '/zones',
      builder: (context, state) => const ZoneDetailsScreen(),
    ),
    GoRoute(
      path: '/weather',
      builder: (context, state) => const WeatherRiskScreen(),
    ),
  ],
);
