# Executive COO Dashboard - Design Specification

## Overview

A real-time executive dashboard for the AI-powered Digital COO system, providing C-suite visibility into business health, AI insights, and actionable recommendations.

---

## Design Principles

1. **Executive-First**: Information density optimized for C-suite decision-making
2. **Real-Time**: Live updates via WebSocket connections
3. **Action-Oriented**: Every insight leads to a clear action
4. **Mobile-Responsive**: Accessible on tablets and mobile devices
5. **Accessible**: WCAG 2.1 AA compliant

---

## Page Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EXECUTIVE COO DASHBOARD                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Business   │  │   Revenue    │  │     Risk     │             │
│  │    Health    │  │   Forecast   │  │    Score     │             │
│  │    Score     │  │              │  │              │             │
│  │              │  │              │  │              │             │
│  │     92/100   │  │   $12.5M     │  │    15/25     │             │
│  │   ↑ +3 pts   │  │   ↑ +8.2%   │  │   ↓ -2 pts   │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Employee   │  │Supply Chain  │  │    Active    │             │
│  │    Health    │  │    Status    │  │    Alerts    │             │
│  │              │  │              │  │              │             │
│  │     85/100   │  │   Healthy    │  │      3       │             │
│  │   ↓ -2 pts   │  │   98% OTD    │  │  1 Critical  │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                      AI RECOMMENDATIONS                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  🎯 Priority 1: Implement Automated Vendor Approval                 │
│     ROI: 3.3x | Cost: $150K | Timeline: 90 days                    │
│     [View Details] [Approve] [Simulate]                            │
│                                                                      │
│  🎯 Priority 2: Augment Legal Team Resources                        │
│     ROI: 1.3x | Cost: $300K | Timeline: 60 days                    │
│     [View Details] [Approve] [Simulate]                            │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                      BUSINESS SIMULATIONS                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📊 What if marketing budget reduced by 10%?                        │
│     Net Impact: $0 | Confidence: 82% | Risk: Medium                │
│     [View Results] [Run New Simulation]                            │
│                                                                      │
│  📊 What if new supplier onboarded?                                 │
│     Net Impact: +$600K | Confidence: 78% | Risk: Low               │
│     [View Results] [Run New Simulation]                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Wireframes

### 1. **Dashboard Overview (Desktop)**

```
┌────────────────────────────────────────────────────────────────────────────┐
│  [Logo] Enterprise Digital COO                    [Profile] [Settings] [?] │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ BUSINESS HEALTH ──────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │ Business │  │ Revenue  │  │   Risk   │  │ Employee │          │   │
│  │  │  Health  │  │ Forecast │  │  Score   │  │  Health  │          │   │
│  │  │          │  │          │  │          │  │          │          │   │
│  │  │  92/100  │  │  $12.5M  │  │  15/25   │  │  85/100  │          │   │
│  │  │  ↑ +3    │  │  ↑ +8.2% │  │  ↓ -2    │  │  ↓ -2    │          │   │
│  │  │          │  │          │  │          │  │          │          │   │
│  │  │ [Chart]  │  │ [Chart]  │  │ [Chart]  │  │ [Chart]  │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │   │
│  │                                                                      │   │
│  │  ┌──────────┐  ┌──────────┐                                        │   │
│  │  │  Supply  │  │  Active  │                                        │   │
│  │  │  Chain   │  │  Alerts  │                                        │   │
│  │  │          │  │          │                                        │   │
│  │  │ Healthy  │  │    3     │                                        │   │
│  │  │ 98% OTD  │  │1 Critical│                                        │   │
│  │  │          │  │          │                                        │   │
│  │  │ [Status] │  │  [List]  │                                        │   │
│  │  └──────────┘  └──────────┘                                        │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─ AI RECOMMENDATIONS ────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  🎯 Priority 1: Implement Automated Vendor Approval System         │   │
│  │     Expected ROI: 3.3x | Cost: $150K | Timeline: 90 days          │   │
│  │     Confidence: 89% | Risk: Medium                                 │   │
│  │     [View Details] [Approve] [Reject] [Simulate Impact]           │   │
│  │                                                                      │   │
│  │  🎯 Priority 2: Augment Legal Team Resources                       │   │
│  │     Expected ROI: 1.3x | Cost: $300K | Timeline: 60 days          │   │
│  │     Confidence: 85% | Risk: Low                                    │   │
│  │     [View Details] [Approve] [Reject] [Simulate Impact]           │   │
│  │                                                                      │   │
│  │  🎯 Priority 3: Streamline Procurement Process                     │   │
│  │     Expected ROI: 2.1x | Cost: $75K | Timeline: 45 days           │   │
│  │     Confidence: 92% | Risk: Low                                    │   │
│  │     [View Details] [Approve] [Reject] [Simulate Impact]           │   │
│  │                                                                      │   │
│  │  [View All Recommendations (12)]                                   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─ BUSINESS SIMULATIONS ──────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  📊 Recent Simulation: Marketing Budget Reduction                  │   │
│  │     Scenario: Reduce marketing budget by 10% ($100K)              │   │
│  │     Net Impact: $0 | Revenue: -5% | Cost: -10%                    │   │
│  │     Confidence: 82% | Risk: Medium (+2 points)                    │   │
│  │     Recommendation: GO WITH CAUTION                                │   │
│  │     [View Full Results] [Run Similar] [Export Report]             │   │
│  │                                                                      │   │
│  │  📊 Recent Simulation: New Supplier Onboarding                     │   │
│  │     Scenario: Onboard new supplier for Product SKU-12345          │   │
│  │     Net Impact: +$600K | Revenue: +2% | Cost: -8%                 │   │
│  │     Confidence: 78% | Risk: Low (+3 points)                       │   │
│  │     Recommendation: GO                                             │   │
│  │     [View Full Results] [Run Similar] [Export Report]             │   │
│  │                                                                      │   │
│  │  [+ Run New Simulation] [View All Simulations (24)]               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─ ACTIVE WORKFLOWS ──────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  ⚙️ Revenue Drop Investigation (Running)                           │   │
│  │     Started: 2 hours ago | Progress: 75%                           │   │
│  │     Agents: Sales ✓ Finance ✓ Supply Chain ✓ Executive ⏳         │   │
│  │     [View Progress] [View Logs]                                    │   │
│  │                                                                      │   │
│  │  ⚙️ Inventory Stockout Analysis (Pending Approval)                │   │
│  │     Started: 30 minutes ago | Awaiting: Your approval              │   │
│  │     Recommendation: Expedite supplier order ($250K)                │   │
│  │     [Approve] [Reject] [View Details]                              │   │
│  │                                                                      │   │
│  │  [View All Workflows (8)]                                          │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### 2. **Mobile View (Responsive)**

```
┌──────────────────────────┐
│ [☰] Digital COO    [👤] │
├──────────────────────────┤
│                          │
│  Business Health         │
│  ┌────────────────────┐  │
│  │      92/100        │  │
│  │      ↑ +3 pts      │  │
│  │   [Mini Chart]     │  │
│  └────────────────────┘  │
│                          │
│  Revenue Forecast        │
│  ┌────────────────────┐  │
│  │     $12.5M         │  │
│  │     ↑ +8.2%        │  │
│  │   [Mini Chart]     │  │
│  └────────────────────┘  │
│                          │
│  Risk Score              │
│  ┌────────────────────┐  │
│  │      15/25         │  │
│  │      ↓ -2 pts      │  │
│  │   [Mini Chart]     │  │
│  └────────────────────┘  │
│                          │
│  [View All Metrics]      │
│                          │
│  AI Recommendations (3)  │
│  ┌────────────────────┐  │
│  │ 🎯 Vendor Approval │  │
│  │    ROI: 3.3x       │  │
│  │    [Details]       │  │
│  └────────────────────┘  │
│                          │
│  [View All]              │
│                          │
└──────────────────────────┘
```

---

## Component Architecture

### **Directory Structure**

```
frontend/
├── app/
│   ├── layout.tsx                 # Root layout
│   ├── page.tsx                   # Dashboard home
│   ├── recommendations/
│   │   └── page.tsx              # Recommendations page
│   ├── simulations/
│   │   ├── page.tsx              # Simulations list
│   │   └── [id]/
│   │       └── page.tsx          # Simulation details
│   ├── workflows/
│   │   ├── page.tsx              # Workflows list
│   │   └── [id]/
│   │       └── page.tsx          # Workflow details
│   └── alerts/
│       └── page.tsx              # Alerts page
│
├── components/
│   ├── dashboard/
│   │   ├── BusinessHealthCard.tsx
│   │   ├── RevenueForecastCard.tsx
│   │   ├── RiskScoreCard.tsx
│   │   ├── EmployeeHealthCard.tsx
│   │   ├── SupplyChainCard.tsx
│   │   ├── ActiveAlertsCard.tsx
│   │   └── MetricsGrid.tsx
│   │
│   ├── recommendations/
│   │   ├── RecommendationCard.tsx
│   │   ├── RecommendationList.tsx
│   │   ├── RecommendationDetails.tsx
│   │   └── ApprovalModal.tsx
│   │
│   ├── simulations/
│   │   ├── SimulationCard.tsx
│   │   ├── SimulationList.tsx
│   │   ├── SimulationResults.tsx
│   │   ├── SimulationForm.tsx
│   │   └── ImpactChart.tsx
│   │
│   ├── workflows/
│   │   ├── WorkflowCard.tsx
│   │   ├── WorkflowList.tsx
│   │   ├── WorkflowProgress.tsx
│   │   └── AgentStatus.tsx
│   │
│   ├── charts/
│   │   ├── LineChart.tsx
│   │   ├── BarChart.tsx
│   │   ├── GaugeChart.tsx
│   │   ├── SparklineChart.tsx
│   │   └── DistributionChart.tsx
│   │
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Modal.tsx
│   │   ├── Tooltip.tsx
│   │   └── LoadingSpinner.tsx
│   │
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       ├── Footer.tsx
│       └── PageContainer.tsx
│
├── lib/
│   ├── api/
│   │   ├── client.ts             # API client
│   │   ├── endpoints.ts          # API endpoints
│   │   └── websocket.ts          # WebSocket client
│   │
│   ├── hooks/
│   │   ├── useMetrics.ts
│   │   ├── useRecommendations.ts
│   │   ├── useSimulations.ts
│   │   ├── useWorkflows.ts
│   │   └── useWebSocket.ts
│   │
│   ├── types/
│   │   ├── metrics.ts
│   │   ├── recommendations.ts
│   │   ├── simulations.ts
│   │   └── workflows.ts
│   │
│   └── utils/
│       ├── formatters.ts
│       ├── calculations.ts
│       └── validators.ts
│
├── styles/
│   ├── globals.css
│   └── themes/
│       ├── light.css
│       └── dark.css
│
└── public/
    ├── icons/
    └── images/
```

---

## Core Components

### 1. **BusinessHealthCard.tsx**

```typescript
'use client';

import { Card } from '@/components/ui/Card';
import { GaugeChart } from '@/components/charts/GaugeChart';
import { SparklineChart } from '@/components/charts/SparklineChart';
import { Badge } from '@/components/ui/Badge';
import { useMetrics } from '@/lib/hooks/useMetrics';

interface BusinessHealthCardProps {
  className?: string;
}

export function BusinessHealthCard({ className }: BusinessHealthCardProps) {
  const { businessHealth, isLoading } = useMetrics();

  if (isLoading) return <Card className={className}>Loading...</Card>;

  const { score, change, trend, breakdown } = businessHealth;

  return (
    <Card className={className}>
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold">Business Health</h3>
        <Badge variant={change > 0 ? 'success' : 'warning'}>
          {change > 0 ? '↑' : '↓'} {Math.abs(change)} pts
        </Badge>
      </div>

      <div className="flex items-center justify-center mb-6">
        <GaugeChart
          value={score}
          max={100}
          size={200}
          color={score >= 80 ? 'green' : score >= 60 ? 'yellow' : 'red'}
        />
      </div>

      <div className="text-center mb-4">
        <div className="text-4xl font-bold">{score}/100</div>
        <div className="text-sm text-gray-500">Overall Score</div>
      </div>

      <div className="mb-4">
        <SparklineChart data={trend} height={40} />
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Revenue Health</span>
          <span className="font-medium">{breakdown.revenue}/100</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Operational Health</span>
          <span className="font-medium">{breakdown.operational}/100</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Financial Health</span>
          <span className="font-medium">{breakdown.financial}/100</span>
        </div>
      </div>

      <button className="w-full mt-4 text-sm text-blue-600 hover:text-blue-800">
        View Detailed Report →
      </button>
    </Card>
  );
}
```

### 2. **RecommendationCard.tsx**

```typescript
'use client';

import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useState } from 'react';
import { ApprovalModal } from './ApprovalModal';

interface Recommendation {
  id: string;
  title: string;
  description: string;
  priority: number;
  estimatedROI: number;
  estimatedCost: number;
  timelineDays: number;
  confidence: number;
  riskLevel: 'low' | 'medium' | 'high';
}

interface RecommendationCardProps {
  recommendation: Recommendation;
  onApprove?: (id: string) => void;
  onReject?: (id: string) => void;
}

export function RecommendationCard({
  recommendation,
  onApprove,
  onReject,
}: RecommendationCardProps) {
  const [showApprovalModal, setShowApprovalModal] = useState(false);

  const {
    id,
    title,
    description,
    priority,
    estimatedROI,
    estimatedCost,
    timelineDays,
    confidence,
    riskLevel,
  } = recommendation;

  return (
    <>
      <Card className="hover:shadow-lg transition-shadow">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🎯</span>
            <Badge variant="primary">Priority {priority}</Badge>
          </div>
          <Badge
            variant={
              riskLevel === 'low'
                ? 'success'
                : riskLevel === 'medium'
                ? 'warning'
                : 'danger'
            }
          >
            {riskLevel.toUpperCase()} RISK
          </Badge>
        </div>

        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-gray-600 mb-4 line-clamp-2">{description}</p>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <div className="text-sm text-gray-500">Expected ROI</div>
            <div className="text-2xl font-bold text-green-600">
              {estimatedROI.toFixed(1)}x
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Investment</div>
            <div className="text-2xl font-bold">
              ${(estimatedCost / 1000).toFixed(0)}K
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Timeline</div>
            <div className="text-lg font-medium">{timelineDays} days</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Confidence</div>
            <div className="text-lg font-medium">{confidence}%</div>
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            variant="primary"
            className="flex-1"
            onClick={() => setShowApprovalModal(true)}
          >
            Approve
          </Button>
          <Button
            variant="outline"
            className="flex-1"
            onClick={() => onReject?.(id)}
          >
            Reject
          </Button>
          <Button variant="ghost" onClick={() => {}}>
            Simulate
          </Button>
        </div>
      </Card>

      {showApprovalModal && (
        <ApprovalModal
          recommendation={recommendation}
          onClose={() => setShowApprovalModal(false)}
          onConfirm={() => {
            onApprove?.(id);
            setShowApprovalModal(false);
          }}
        />
      )}
    </>
  );
}
```

### 3. **SimulationResults.tsx**

```typescript
'use client';

import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { DistributionChart } from '@/components/charts/DistributionChart';
import { BarChart } from '@/components/charts/BarChart';

interface SimulationResult {
  simulationId: string;
  scenario: {
    type: string;
    description: string;
  };
  revenueImpact: {
    bestCase: number;
    mostLikely: number;
    worstCase: number;
    percentageChange: number;
  };
  costImpact: {
    bestCase: number;
    mostLikely: number;
    worstCase: number;
    percentageChange: number;
  };
  riskImpact: {
    riskScoreChange: number;
  };
  netFinancialImpact: number;
  overallRecommendation: string;
  confidenceScore: number;
  keyInsights: string[];
}

interface SimulationResultsProps {
  result: SimulationResult;
}

export function SimulationResults({ result }: SimulationResultsProps) {
  const {
    scenario,
    revenueImpact,
    costImpact,
    riskImpact,
    netFinancialImpact,
    overallRecommendation,
    confidenceScore,
    keyInsights,
  } = result;

  const getRecommendationColor = (rec: string) => {
    if (rec.startsWith('GO -')) return 'success';
    if (rec.startsWith('GO WITH')) return 'warning';
    if (rec.startsWith('CONDITIONAL')) return 'warning';
    return 'danger';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold mb-2">{scenario.description}</h2>
            <Badge variant="secondary">{scenario.type}</Badge>
          </div>
          <Badge variant={getRecommendationColor(overallRecommendation)}>
            {overallRecommendation.split(' - ')[0]}
          </Badge>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-500 mb-1">Net Impact</div>
            <div
              className={`text-3xl font-bold ${
                netFinancialImpact > 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              ${(netFinancialImpact / 1000).toFixed(0)}K
            </div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-500 mb-1">Confidence</div>
            <div className="text-3xl font-bold">{confidenceScore}%</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-500 mb-1">Risk Change</div>
            <div
              className={`text-3xl font-bold ${
                riskImpact.riskScoreChange > 0 ? 'text-red-600' : 'text-green-600'
              }`}
            >
              {riskImpact.riskScoreChange > 0 ? '+' : ''}
              {riskImpact.riskScoreChange}
            </div>
          </div>
        </div>
      </Card>

      {/* Impact Analysis */}
      <div className="grid grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-semibold mb-4">Revenue Impact</h3>
          <DistributionChart
            bestCase={revenueImpact.bestCase}
            mostLikely={revenueImpact.mostLikely}
            worstCase={revenueImpact.worstCase}
            height={200}
          />
          <div className="mt-4 text-center">
            <div className="text-2xl font-bold">
              {revenueImpact.percentageChange > 0 ? '+' : ''}
              {revenueImpact.percentageChange.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-500">Expected Change</div>
          </div>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold mb-4">Cost Impact</h3>
          <DistributionChart
            bestCase={costImpact.bestCase}
            mostLikely={costImpact.mostLikely}
            worstCase={costImpact.worstCase}
            height={200}
          />
          <div className="mt-4 text-center">
            <div className="text-2xl font-bold">
              {costImpact.percentageChange > 0 ? '+' : ''}
              {costImpact.percentageChange.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-500">Expected Change</div>
          </div>
        </Card>
      </div>

      {/* Key Insights */}
      <Card>
        <h3 className="text-lg font-semibold mb-4">Key Insights</h3>
        <ul className="space-y-2">
          {keyInsights.map((insight, index) => (
            <li key={index} className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">•</span>
              <span>{insight}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
```

---

## API Integration

### **useMetrics Hook**

```typescript
'use client';

import { useState, useEffect } from 'react';
import { useWebSocket } from './useWebSocket';
import { apiClient } from '@/lib/api/client';

interface BusinessMetrics {
  businessHealth: {
    score: number;
    change: number;
    trend: number[];
    breakdown: {
      revenue: number;
      operational: number;
      financial: number;
    };
  };
  revenueForecast: {
    current: number;
    forecast: number;
    change: number;
    trend: number[];
  };
  riskScore: {
    score: number;
    change: number;
    breakdown: {
      operational: number;
      financial: number;
      strategic: number;
    };
  };
  employeeHealth: {
    score: number;
    change: number;
    turnover: number;
    engagement: number;
  };
  supplyChain: {
    status: 'healthy' | 'warning' | 'critical';
    onTimeDelivery: number;
    inventoryHealth: number;
  };
  activeAlerts: {
    total: number;
    critical: number;
    high: number;
    medium: number;
  };
}

export function useMetrics() {
  const [metrics, setMetrics] = useState<BusinessMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // WebSocket for real-time updates
  const { lastMessage } = useWebSocket('/ws/metrics');

  // Initial fetch
  useEffect(() => {
    async function fetchMetrics() {
      try {
        const data = await apiClient.get<BusinessMetrics>('/api/v1/metrics');
        setMetrics(data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchMetrics();
  }, []);

  // Update from WebSocket
  useEffect(() => {
    if (lastMessage) {
      setMetrics((prev) => ({
        ...prev,
        ...lastMessage,
      }));
    }
  }, [lastMessage]);

  return {
    ...metrics,
    isLoading,
    error,
  };
}
```

---

## User Journey

### **Journey 1: Executive Reviews Dashboard**

```
1. Executive opens dashboard
   ↓
2. Views Business Health Score (92/100, ↑ +3)
   ↓
3. Notices Active Alerts (3, 1 Critical)
   ↓
4. Clicks on Critical Alert
   ↓
5. Views "Revenue Drop Investigation" workflow
   ↓
6. Sees AI recommendation: "Implement Automated Vendor Approval"
   ↓
7. Clicks "Simulate Impact"
   ↓
8. Reviews simulation: Net Impact +$450K, ROI 3.3x
   ↓
9. Clicks "Approve"
   ↓
10. Workflow initiated, receives confirmation
```

### **Journey 2: Run Business Simulation**

```
1. Executive clicks "Run New Simulation"
   ↓
2. Selects scenario type: "Budget Change"
   ↓
3. Enters parameters: "Reduce marketing budget by 10%"
   ↓
4. Sets baseline metrics (auto-populated from current data)
   ↓
5. Clicks "Run Simulation"
   ↓
6. Waits 8 seconds (progress indicator shown)
   ↓
7. Views results:
   - Net Impact: $0
   - Revenue: -5%
   - Cost: -10%
   - Risk: +2 points
   - Recommendation: GO WITH CAUTION
   ↓
8. Reviews key insights and recommended actions
   ↓
9. Exports report as PDF
   ↓
10. Shares with leadership team
```

### **Journey 3: Approve AI Recommendation**

```
1. Executive sees Priority 1 recommendation
   ↓
2. Clicks "View Details"
   ↓
3. Reviews:
   - Full description
   - ROI analysis
   - Implementation plan
   - Risk assessment
   - Success metrics
   ↓
4. Clicks "Simulate Impact" to validate
   ↓
5. Reviews simulation results
   ↓
6. Satisfied with analysis, clicks "Approve"
   ↓
7. Approval modal appears with summary
   ↓
8. Confirms approval with digital signature
   ↓
9. Workflow initiated automatically
   ↓
10. Receives email confirmation and tracking link
```

---

## Technology Stack

### **Frontend**
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts / Chart.js
- **State Management**: React Context + SWR
- **Real-time**: WebSocket (native)
- **Forms**: React Hook Form + Zod
- **Testing**: Jest + React Testing Library

### **UI Components**
- **Base**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Tables**: TanStack Table

### **Build & Deploy**
- **Build**: Turbopack
- **Deploy**: Vercel / Docker
- **CI/CD**: GitHub Actions

---

## Responsive Breakpoints

```css
/* Mobile First */
sm: 640px   /* Small devices */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large screens */
```

---

## Accessibility Features

1. **Keyboard Navigation**: Full keyboard support
2. **Screen Readers**: ARIA labels and roles
3. **Color Contrast**: WCAG AA compliant
4. **Focus Indicators**: Visible focus states
5. **Alt Text**: All images and charts
6. **Semantic HTML**: Proper heading hierarchy

---

## Performance Targets

- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **WebSocket Latency**: < 100ms

---

## Summary

**Complete Executive Dashboard Design** with:

✅ **8 Key Metrics** displayed prominently
✅ **Real-Time Updates** via WebSocket
✅ **AI Recommendations** with approval workflow
✅ **Business Simulations** with visual results
✅ **Active Workflows** monitoring
✅ **Responsive Design** (mobile, tablet, desktop)
✅ **Next.js 14 Architecture** with TypeScript
✅ **Component Library** (20+ reusable components)
✅ **User Journeys** mapped out
✅ **Accessibility** WCAG 2.1 AA compliant

**Status**: ✅ Design Complete - Ready for Implementation