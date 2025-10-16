'use client';

import { useEffect, useState } from 'react';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface UsageRecord {
  package: string;
  time_used_ms: number;
  timestamp: string;
  app_name?: string;
}

interface UsageData {
  records: UsageRecord[];
  last_updated: string | null;
}

interface AppSummary {
  package: string;
  total_time_ms: number;
  total_time_hours: number;
}

export default function Dashboard() {
  const [usageData, setUsageData] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await fetch('/data/usage_data.json');

      if (!response.ok) {
        throw new Error('No data file found. Run the Python script to collect data first.');
      }

      const data: UsageData = await response.json();
      setUsageData(data);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      setLoading(false);
    }
  };

  const getAppSummary = (): AppSummary[] => {
    if (!usageData || !usageData.records) return [];

    const summary: { [key: string]: number } = {};

    usageData.records.forEach((record) => {
      const pkg = record.package;
      const time = record.time_used_ms || 0;

      if (summary[pkg]) {
        summary[pkg] += time;
      } else {
        summary[pkg] = time;
      }
    });

    return Object.entries(summary)
      .map(([pkg, time_ms]) => ({
        package: pkg,
        total_time_ms: time_ms,
        total_time_hours: time_ms / (1000 * 60 * 60),
      }))
      .sort((a, b) => b.total_time_ms - a.total_time_ms);
  };

  const formatTime = (ms: number): string => {
    const hours = Math.floor(ms / (1000 * 60 * 60));
    const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const getTotalTime = (): number => {
    if (!usageData) return 0;
    return usageData.records.reduce((sum, record) => sum + (record.time_used_ms || 0), 0);
  };

  const getChartData = () => {
    const summary = getAppSummary().slice(0, 10); // Top 10 apps

    return {
      labels: summary.map((app) => app.package.split('.').pop() || app.package),
      datasets: [
        {
          label: 'Usage Time (hours)',
          data: summary.map((app) => app.total_time_hours),
          backgroundColor: [
            '#1a73e8',
            '#34a853',
            '#fbbc04',
            '#ea4335',
            '#8e24aa',
            '#00acc1',
            '#f57c00',
            '#7cb342',
            '#c0ca33',
            '#5e35b1',
          ],
        },
      ],
    };
  };

  if (loading) {
    return (
      <div className="container">
        <header>
          <h1>Phone Usage Dashboard</h1>
        </header>
        <div className="loading">Loading data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <header>
          <h1>Phone Usage Dashboard</h1>
        </header>
        <div className="error">
          <strong>Error:</strong> {error}
          <p style={{ marginTop: '10px', fontSize: '0.9em' }}>
            Make sure you have run the Python data collection script first:
            <br />
            <code style={{ background: '#f5f5f5', padding: '5px', borderRadius: '3px' }}>
              python backend/collect_usage.py
            </code>
          </p>
        </div>
      </div>
    );
  }

  const appSummary = getAppSummary();
  const totalTime = getTotalTime();
  const totalApps = appSummary.length;
  const recordCount = usageData?.records.length || 0;

  return (
    <div className="container">
      <header>
        <h1>Phone Usage Dashboard</h1>
        {usageData?.last_updated && (
          <p style={{ color: '#666', marginTop: '10px' }}>
            Last updated: {new Date(usageData.last_updated).toLocaleString()}
          </p>
        )}
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Screen Time</h3>
          <div className="stat-value">{formatTime(totalTime)}</div>
        </div>
        <div className="stat-card">
          <h3>Apps Tracked</h3>
          <div className="stat-value">{totalApps}</div>
        </div>
        <div className="stat-card">
          <h3>Total Records</h3>
          <div className="stat-value">{recordCount}</div>
        </div>
        <div className="stat-card">
          <h3>Avg Daily Usage</h3>
          <div className="stat-value">{formatTime(totalTime / 7)}</div>
        </div>
      </div>

      {appSummary.length > 0 ? (
        <>
          <div className="chart-container">
            <h2>Top 10 Most Used Apps (Pie Chart)</h2>
            <div style={{ maxWidth: '500px', margin: '0 auto' }}>
              <Pie data={getChartData()} />
            </div>
          </div>

          <div className="chart-container">
            <h2>Top 10 Most Used Apps (Bar Chart)</h2>
            <Bar
              data={getChartData()}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'Hours',
                    },
                  },
                },
              }}
            />
          </div>

          <div className="app-list">
            <h2>All Apps Usage</h2>
            {appSummary.map((app, index) => (
              <div key={app.package} className="app-item">
                <div>
                  <span style={{ color: '#999', marginRight: '10px' }}>{index + 1}.</span>
                  <span className="app-name">{app.package}</span>
                </div>
                <div className="app-time">{formatTime(app.total_time_ms)}</div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="no-data">No usage data available</div>
      )}
    </div>
  );
}
