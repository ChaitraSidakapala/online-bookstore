# Architecture Decision Record (ADR)

## Overview

This document explains the key architectural decisions made while building this bookstore microservices application. As a learning project, some decisions prioritize simplicity and understanding over production-grade complexity.

---

## 1. Microservices Architecture

### Decision
Split the application into two separate services: Catalog Service (books) and Order Service (orders), rather than building a monolithic application.

### Benefits
- **Independent Development**: Each service can be modified without affecting the other
- **Technology Flexibility**: Could use different tech stacks for each service if needed
- **Scalability**: Services can scale independently based on their load
- **Learning Value**: Demonstrates real-world distributed systems concepts
- **Fault Isolation**: If one service fails, the other can continue operating

### Challenges
- **Complexity**: More moving parts to manage and debug
- **Network Latency**: Services communicate over HTTP, which is slower than in-process calls
- **Data Consistency**: Harder to maintain consistency across services
- **Testing**: Need to test services individually and together

### Mitigation Strategies
- **Implemented**:
  - Simple REST API communication between services
  - Shared database to avoid distributed transaction complexity
  - Comprehensive API documentation (Swagger UI)
  - Health check endpoints for monitoring
  
- **Future Enhancements**:
  - Add retry logic for failed service calls
  - Implement circuit breakers to prevent cascade failures
  - Add request timeouts
  - Consider API Gateway for unified entry point

---

## 2. Shared Database Pattern

### Decision
Use a single PostgreSQL database shared by both services, rather than database-per-service pattern.

### Benefits
- **Simplicity**: Easier to set up and manage one database
- **ACID Guarantees**: PostgreSQL handles data consistency
- **No Distributed Transactions**: Avoid complexity of two-phase commits
- **Development Speed**: Faster to develop and test
- **Learning Focus**: Can focus on Kubernetes concepts rather than distributed data

### Challenges
- **Tight Coupling**: Services are coupled through the database schema
- **Scalability Limits**: Database can become a bottleneck
- **Schema Changes**: Changes affect multiple services
- **Not True Microservices**: Violates the principle of service independence

### Mitigation Strategies
- **Implemented**:
  - Clear separation of tables (books vs orders)
  - Services only access their own tables
  - Documented schema in code comments
  
- **Future Enhancements**:
  - Migrate to database-per-service pattern
  - Implement event-driven architecture
  - Use message queues for async communication
  - Add database migration tools (Alembic)

---

## 3. Kubernetes Deployment

### Decision
Deploy on Kubernetes instead of simpler platforms (Docker Compose, VMs, or serverless).

### Benefits
- **Industry Standard**: Kubernetes is widely used in production
- **Auto-scaling**: HPA enables automatic pod scaling based on load
- **Self-healing**: Automatically restarts failed pods
- **Service Discovery**: Built-in DNS for service-to-service communication
- **Declarative Config**: Infrastructure as code with YAML manifests
- **Cloud Portability**: Can run on any Kubernetes cluster (local, GCP, AWS, Azure)

### Challenges
- **Steep Learning Curve**: Complex system with many concepts
- **Resource Overhead**: Requires more resources than simpler deployments
- **Configuration Complexity**: 14 YAML files to manage
- **Local Development**: Need Docker Desktop or Minikube

### Mitigation Strategies
- **Implemented**:
  - Simplified deployment with deploy.sh script
  - Clear documentation with examples
  - Basic configurations without advanced features
  - Namespace isolation for easy cleanup
  
- **Future Enhancements**:
  - Add Helm charts for templating
  - Implement Kustomize for environment-specific configs
  - Add resource limits and requests
  - Implement health probes (liveness/readiness)

---

## 4. Security Approach

### Decision
Implement basic security suitable for a learning project, avoiding production-level complexity.

### Current Security Measures

#### ✅ Implemented
1. **Database Credentials**
   - Stored in Kubernetes Secrets (base64 encoded)
   - Injected as environment variables
   - Not hardcoded in application code

2. **Namespace Isolation**
   - Resources deployed in dedicated `bookstore` namespace
   - Provides logical separation from other workloads

3. **Service-to-Service Communication**
   - ClusterIP services (internal only, not exposed externally)
   - Services communicate via Kubernetes DNS

4. **Container Images**
   - Using official Python base images
   - Dependencies specified in requirements.txt

### Security Challenges

#### ❌ Not Implemented (Learning Project Trade-offs)

1. **No Authentication/Authorization**
   - APIs are publicly accessible without login
   - **Risk**: Anyone can create, modify, or delete data
   - **Production Need**: JWT tokens, OAuth2, or API keys

2. **No Network Policies**
   - All pods can communicate with each other
   - **Risk**: Lateral movement if one service is compromised
   - **Production Need**: Restrict pod-to-pod traffic

3. **No TLS/HTTPS**
   - All communication is unencrypted HTTP
   - **Risk**: Data can be intercepted in transit
   - **Production Need**: TLS certificates, encrypted connections

4. **No RBAC (Role-Based Access Control)**
   - Pods use default service account
   - **Risk**: Pods might have unnecessary Kubernetes API access
   - **Production Need**: Minimal permission service accounts

5. **Secrets in Git (Base64)**
   - Kubernetes secrets are base64 encoded (not encrypted)
   - Secret files committed to repository
   - **Risk**: Secrets exposed if repository is public
   - **Production Need**: External secret management (Vault, AWS Secrets Manager)

6. **No Input Validation Beyond Pydantic**
   - Basic validation but no SQL injection protection layers
   - **Risk**: Potential injection attacks
   - **Production Need**: Parameterized queries (SQLAlchemy ORM helps), input sanitization

7. **No Rate Limiting**
   - No protection against abuse or DDoS
   - **Risk**: Service can be overwhelmed
   - **Production Need**: API Gateway with rate limiting

8. **No Container Security**
   - Containers might run as root
   - No security context constraints
   - **Risk**: Container breakout vulnerabilities
   - **Production Need**: Non-root users, read-only filesystems, seccomp profiles

### Mitigation Strategies

#### Immediate Improvements (Without Major Complexity)
1. Add simple API key authentication
2. Run containers as non-root user
3. Add basic rate limiting middleware
4. Use .gitignore for secrets (use ConfigMaps for non-sensitive config)
5. Add SQL injection testing

---

## 5. Horizontal Pod Autoscaler (HPA)

### Decision
Configure HPA for both services to demonstrate auto-scaling capabilities.

### Benefits
- **Automatic Scaling**: Pods scale based on CPU/Memory usage
- **Cost Efficiency**: Scale down during low traffic
- **High Availability**: Scale up during high traffic
- **Learning Value**: Demonstrates Kubernetes scaling features

### Challenges
- **Metrics Server Required**: Local clusters may not have it installed
- **Configuration Complexity**: Need to tune min/max replicas and thresholds
- **Resource Overhead**: Multiple replicas use more resources
- **Cold Start**: New pods take time to start

### Current Configuration
- **Catalog Service**: 2-5 replicas (70% CPU, 80% Memory)
- **Order Service**: 2-10 replicas (70% CPU, 80% Memory)

### Mitigation Strategies
- **Implemented**:
  - Conservative min replicas (2) for basic HA
  - Documented that metrics-server is needed
  - Manual scaling instructions as fallback
  
- **Future Enhancements**:
  - Install metrics-server for local testing
  - Add custom metrics (request rate, queue depth)
  - Fine-tune thresholds based on load testing
  - Implement Vertical Pod Autoscaler (VPA)

---

## 6. Persistent Storage

### Decision
Use StatefulSet with PersistentVolume for PostgreSQL instead of ephemeral storage.

### Benefits
- **Data Persistence**: Data survives pod restarts
- **StatefulSet Benefits**: Stable network identity, ordered deployment
- **Production-like**: Mirrors real database deployments

### Challenges
- **Complexity**: More complex than simple Deployment
- **Storage Classes**: Need to configure storage provisioning
- **Backup**: No automated backup strategy
- **Single Point of Failure**: Only one database instance

### Mitigation Strategies
- **Implemented**:
  - 5Gi PersistentVolumeClaim
  - StatefulSet with stable pod name (postgres-0)
  - Init script to load sample data
  
- **Future Enhancements**:
  - Add database replication (primary/replica)
  - Implement automated backups
  - Add disaster recovery plan
  - Use managed database service (RDS, Cloud SQL)

---

## 7. Deployment Automation

### Decision
Create deployment script (deploy.sh) for one-command setup.

### Benefits
- **Ease of Use**: Single command to deploy everything
- **Consistency**: Same process every time
- **Documentation**: Script serves as executable documentation
- **Fast Iteration**: Quick teardown and rebuild

### Challenges
- **Platform Specific**: Bash script works on Unix/Mac but not Windows
- **Error Handling**: Limited error recovery
- **No Rollback**: Can't easily undo failed deployments

### Mitigation Strategies
- **Implemented**:
  - Clear output messages and progress indicators
  - Prerequisite checks (Docker, kubectl)
  - Cleanup script for easy reset
  
- **Future Enhancements**:
  - Add Windows PowerShell version
  - Implement better error handling
  - Add deployment validation tests
  - Consider CI/CD pipeline (GitHub Actions)

---

## 8. Technology Choices

### Python + FastAPI
**Why**: Modern, fast, easy to learn, excellent documentation generation

**Alternatives Considered**: 
- Node.js/Express (more JavaScript-heavy)
- Java/Spring Boot (more enterprise-focused, steeper learning curve)
- Go (better performance but harder to learn)

### PostgreSQL
**Why**: Popular, robust, ACID compliant, good for learning SQL

**Alternatives Considered**:
- MongoDB (NoSQL, but wanted to learn relational DB)
- MySQL (similar to PostgreSQL, chose Postgres for JSON support)
- SQLite (too simple for learning Kubernetes)

### Docker
**Why**: Industry standard for containerization, required for Kubernetes

**No Alternative**: Essential for this architecture

### Kubernetes
**Why**: Learn industry-standard orchestration platform

**Alternatives Considered**:
- Docker Compose (too simple, limited scaling)
- Serverless (less control, harder to learn internals)
- VMs (old-school, too much overhead)

---

## Summary of Trade-offs

### Chose Simplicity Over:
- ❌ Database per service (easier to manage one DB)
- ❌ Advanced security (authentication, encryption, RBAC)
- ❌ Production monitoring (Prometheus, Grafana)
- ❌ CI/CD pipeline (manual deployment is fine for learning)
- ❌ Advanced error handling (circuit breakers, retries)

### Chose Learning Value Over:
- ❌ Serverless simplicity (wanted to learn Kubernetes)
- ❌ Monolithic simplicity (wanted to learn microservices)
- ❌ Managed services (wanted to understand internals)

### Successfully Balanced:
- ✅ Microservices architecture without excessive complexity
- ✅ Kubernetes orchestration with basic features
- ✅ Auto-scaling configuration (HPA)
- ✅ Persistent storage
- ✅ Service communication patterns
- ✅ Good documentation and automation

---

## Lessons Learned

### What Worked Well
1. Starting with simple architecture and adding features incrementally
2. Comprehensive documentation alongside code
3. Automation scripts for deployment and cleanup
4. Using FastAPI's auto-generated API docs
5. Namespace isolation for easy management

### What Would I Do Differently
1. **Security First**: Would add at least basic authentication earlier
2. **Testing**: Should have added integration tests from the start
3. **Observability**: Would add logging and monitoring sooner
4. **Schema Planning**: Better database design upfront
5. **Error Handling**: More robust error handling in service communication

### Next Steps for Improvement
1. Add authentication (JWT or API keys)
2. Implement integration tests
3. Add monitoring (Prometheus + Grafana)
4. Separate databases per service
5. Add message queue (RabbitMQ or Kafka)
6. Implement CI/CD pipeline
7. Add caching layer (Redis)
8. Better security hardening

---

## Conclusion

This architecture represents a learning-focused approach to building microservices on Kubernetes. While it intentionally omits production-grade features for simplicity, it successfully demonstrates:

- ✅ Core microservices patterns
- ✅ Kubernetes orchestration fundamentals
- ✅ Service communication
- ✅ Auto-scaling concepts
- ✅ Persistent storage
- ✅ Container deployment

