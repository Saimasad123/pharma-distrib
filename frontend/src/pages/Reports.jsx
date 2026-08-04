import { useEffect, useState } from "react";
import {
  getProfitReport,
  getRevenueReport,
  getMonthlyReport,
  getAnnualReport,
} from "../api/reports";
import { getMonthlySalesAnalytics } from "../api/analytics";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";

function Reports() {
  const today = new Date();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [profit, setProfit] = useState(null);
  const [revenue, setRevenue] = useState(null);
  const [monthly, setMonthly] = useState(null);
  const [annual, setAnnual] = useState(null);
  const [annualSeries, setAnnualSeries] = useState([]);
  const [monthlySeries, setMonthlySeries] = useState([]);

  const formatCurrency = (value) =>
    `Rs. ${Number(value || 0).toLocaleString()}`;

  const buildAnnualYears = () => {
    return Array.from({ length: 5 }, (_, index) => year - 4 + index);
  };

  const loadAnnualSeries = async (years) => {
    const series = await Promise.all(
      years.map((targetYear) => getAnnualReport(targetYear))
    );

    return years.map((targetYear, index) => ({
      year: targetYear,
      revenue: series[index]?.revenue || 0,
      cost: series[index]?.cost || 0,
      profit: series[index] ? Number(series[index].revenue || 0) - Number(series[index].cost || 0) : 0,
    }));
  };

  const loadReports = async () => {
    try {
      setLoading(true);
      setError("");

      const currentYears = buildAnnualYears();

      const [profitData, revenueData, monthlyData, annualData, annualChartData, monthlySalesData] =
        await Promise.all([
          getProfitReport(),
          getRevenueReport(),
          getMonthlyReport(year, month),
          getAnnualReport(year),
          loadAnnualSeries(currentYears),
          getMonthlySalesAnalytics(year),
        ]);

      setProfit(profitData);
      setRevenue(revenueData);
      setMonthly(monthlyData);
      setAnnual(annualData);
      setAnnualSeries(annualChartData);
      setMonthlySeries(monthlySalesData.monthly_sales || []);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
          "Failed to load reports."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, [year, month]);

  if (loading) {
    return (
      <div className="page-loading">
        Loading reports...
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Reports</h1>
          <p>Review profit, revenue, and monthly performance.</p>
        </div>
      </div>

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      <div className="form-card">
        <div className="form-grid">
          <div className="form-group">
            <label>Year</label>
            <input
              type="number"
              min="2000"
              max="2100"
              value={year}
              onChange={(event) =>
                setYear(Number(event.target.value))
              }
            />
          </div>

          <div className="form-group">
            <label>Month</label>
            <select
              value={month}
              onChange={(event) =>
                setMonth(Number(event.target.value))
              }
            >
              {Array.from({ length: 12 }, (_, index) => index + 1).map(
                (value) => (
                  <option key={value} value={value}>
                    {new Date(0, value - 1).toLocaleString("default", {
                      month: "long",
                    })}
                  </option>
                )
              )}
            </select>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Profit Report</h3>
          <p>
            Revenue: Rs. {Number(profit?.total_revenue || 0).toLocaleString()}
          </p>
          <p>
            Cost: Rs. {Number(profit?.total_cost || 0).toLocaleString()}
          </p>
          <p>
            Profit: Rs. {Number(profit?.total_profit || 0).toLocaleString()}
          </p>
        </div>

        <div className="stat-card">
          <h3>Revenue Report</h3>
          <p>
            Total Revenue: Rs. {Number(revenue?.total_revenue || 0).toLocaleString()}
          </p>
        </div>

        <div className="stat-card">
          <h3>Monthly Report</h3>
          <p>
            Month: {monthly?.month}/{monthly?.year}
          </p>
          <p>
            Revenue: Rs. {Number(monthly?.revenue || 0).toLocaleString()}
          </p>
          <p>
            Profit: Rs. {Number((monthly?.revenue || 0) - (monthly?.cost || 0)).toLocaleString()}
          </p>
          <p>Orders: {monthly?.total_orders || 0}</p>
        </div>

        <div className="stat-card">
          <h3>Annual Report</h3>
          <p>Year: {annual?.year || year}</p>
          <p>
            Revenue: Rs. {Number(annual?.revenue || 0).toLocaleString()}
          </p>
          <p>
            Profit: Rs. {Number((annual?.revenue || 0) - (annual?.cost || 0)).toLocaleString()}
          </p>
          <p>Orders: {annual?.total_orders || 0}</p>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Monthly Profit Trend</h3>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart
              data={monthlySeries}
              margin={{ top: 20, right: 20, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="month"
                tickFormatter={(value) =>
                  new Date(0, value - 1).toLocaleString("default", {
                    month: "short",
                  })
                }
              />
              <YAxis />
              <Tooltip
                formatter={(value) => formatCurrency(value)}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#1f78b4"
                name="Revenue"
              />
              <Line
                type="monotone"
                dataKey="cost"
                stroke="#33a02c"
                name="Cost"
              />
              <Line
                type="monotone"
                dataKey="profit"
                stroke="#e31a1c"
                name="Profit"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Annual Profit Trend</h3>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart
              data={annualSeries}
              margin={{ top: 20, right: 20, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip
                formatter={(value) => formatCurrency(value)}
              />
              <Legend />
              <Bar dataKey="profit" fill="#e31a1c" name="Profit" />
              <Bar dataKey="revenue" fill="#1f78b4" name="Revenue" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default Reports;
