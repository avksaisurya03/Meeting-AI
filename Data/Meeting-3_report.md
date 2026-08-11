# Executive Meeting Digest

---

## 📋 Executive Summary

This sync reviewed staging load-test failures and agreed immediate remediation steps to make the platform ready for the Diwali flash sale. Key issues: the primary PostgreSQL database locked up during a 50,000 concurrent-user test due to unindexed foreign keys in the order_items table, causing Spring Boot thread pools to hit 100% utilization; the payment gateway integration lacks a fallback mechanism; the current cache is single-node Memcached. Decisions were made to add composite indexes to foreign-key columns across the checkout schema and to migrate caching to a three-shard Redis Cluster (AWS ElastiCache). Explicit action items were assigned to apply the index migration and re-run load tests, provision and test the Redis cluster, and implement Resilience4j circuit breakers for checkout endpoints. The team emphasized thorough staging testing before Friday's code freeze.


## 🎯 Action Items Matrix

| # | Task Title | Assigned (Role) | Priority | Effort | Timeline | Acceptance Criteria |
|---|------------|-----------------|----------|--------|----------|---------------------|
| 1 | **Apply composite indexes to foreign-key columns in the checkout schema on staging and run a fresh load test** | Pooja (Frontend/Backend representative) | `High` | `Moderate` | By 5 PM today (March 12, 2026) | • Index migration script executed on the staging checkout schema<br>• A fresh load test against staging completed<br>• New performance metrics from the load test shared with the team by 5 PM<br>• No complete PostgreSQL lockup observed during the load test and Spring Boot thread pools do not hit 100% utilization |
| 2 | **Provision and configure a three-shard Redis Cluster on AWS ElastiCache and complete connection testing** | Amit | `High` | `Moderate` | By 11 AM tomorrow (March 13, 2026) | • Three-shard Redis Cluster provisioned on AWS ElastiCache<br>• Application connection testing to the Redis Cluster completed successfully<br>• Confirmation shared that Redis Cluster connectivity is stable |
| 3 | **Implement circuit breaker wrappers (Resilience4j) for checkout API endpoints in the order service** | Pooja (Frontend/Backend representative) | `High` | `Complex` | By Thursday EOD (as stated in meeting) | • Resilience4j circuit breakers implemented for checkout API endpoints in the order service<br>• Circuit breaker behavior exercised in tests and deployed to staging<br>• Evidence that payment/checkout failures are handled via the circuit breaker (fallbacks or controlled degradation) and test results shared |


## 💡 Architecture & Design Decisions

### Decision 1: Add composite indexes to all foreign-key columns across the checkout schema.
**Rationale:** The primary PostgreSQL database locked up during the 50,000 concurrent-user staging test due to unindexed foreign keys in the order_items table; indexing is required immediately to prevent database crashes under peak load.

### Decision 2: Switch caching from single-node Memcached to a Redis Cluster with three shards on AWS ElastiCache.
**Rationale:** A Redis Cluster provides automatic failover and higher read throughput during peak traffic, addressing the single-node Memcached availability and throughput limitations identified for the flash sale.

## ⚠️ Blockers & Risk Log

### Blocker 1: Primary PostgreSQL database locked up during 50,000 concurrent-user load test due to unindexed foreign keys in the order_items table.
**Impact:** Caused full DB lockup and is an unacceptable business risk for the Diwali flash sale; could cause service outages and revenue loss during peak traffic.

### Blocker 2: Spring Boot service thread pools hit 100% utilization within two minutes during the load test.
**Impact:** Service threads saturated leading to degraded or unavailable services under sustained load.

### Blocker 3: Payment gateway integration lacks a fallback mechanism when primary API endpoints fail.
**Impact:** No fallback increases risk of failed payments or checkout failures if the payment provider is unavailable during peak traffic.
