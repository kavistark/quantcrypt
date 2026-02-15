# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import pandas as pd
from typing import Dict, List, Any

from wev.urls import Trade

class TradingAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    broker = models.CharField(max_length=50)
    account_type = models.CharField(max_length=20, choices=[
        ('demo', 'Demo'),
        ('live', 'Live')
    ])
    initial_balance = models.DecimalField(max_digits=12, decimal_places=2)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-close_time', '-open_time']
        indexes = [
            models.Index(fields=['account', 'symbol']),
            models.Index(fields=['close_time']),
            models.Index(fields=['profit']),
        ]

    def __str__(self):
        return f"{self.symbol} {self.side} {self.volume} - {self.profit}"

    @property
    def is_closed(self):
        return self.close_time is not None

    @property
    def duration_hours(self):
        if self.is_closed:
            return (self.close_time - self.open_time).total_seconds() / 3600
        return (timezone.now() - self.open_time).total_seconds() / 3600

    @property
    def pips(self):
        """Calculate pips based on symbol type"""
        if not self.is_closed:
            return 0
        
        price_diff = self.close_price - self.open_price
        if self.side == 'SELL':
            price_diff = -price_diff
            
        # Standard pip calculation (most forex pairs)
        if 'JPY' in self.symbol:
            return float(price_diff * 100)  # JPY pairs
        elif 'XAU' in self.symbol or 'GOLD' in self.symbol:
            return float(price_diff * 10)   # Gold
        else:
            return float(price_diff * 10000)  # Standard forex


# views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

@login_required
def portfolio_dashboard(request):
    """Main portfolio dashboard view"""
    account = get_object_or_404(TradingAccount, user=request.user, is_active=True)
    
    # Get portfolio data
    portfolio_data = PortfolioAnalyzer(account).get_portfolio_summary()
    
    context = {
        'portfolio_data': portfolio_data,
        'account': account,
        'last_updated': timezone.now(),
    }
    
    return render(request, 'trading/portfolio.html', context)

@login_required
def portfolio_api(request):
    """API endpoint for portfolio data"""
    account = get_object_or_404(TradingAccount, user=request.user, is_active=True)
    analyzer = PortfolioAnalyzer(account)
    
    data_type = request.GET.get('type', 'summary')
    
    if data_type == 'summary':
        data = analyzer.get_portfolio_summary()
    elif data_type == 'trades':
        data = analyzer.get_recent_trades()
    elif data_type == 'analytics':
        data = analyzer.get_advanced_analytics()
    elif data_type == 'risk':
        data = analyzer.get_risk_metrics()
    else:
        data = {'error': 'Invalid data type'}
    
    return JsonResponse(data)

@login_required
def upload_trades_csv(request):
    """Upload and process trading CSV file"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        account = get_object_or_404(TradingAccount, user=request.user, is_active=True)
        
        try:
            # Process CSV file
            processor = CSVTradeProcessor(account)
            result = processor.process_csv(csv_file)
            
            return JsonResponse({
                'success': True,
                'processed': result['processed'],
                'skipped': result['skipped'],
                'errors': result['errors']
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# utils.py - Portfolio Analysis Class
class PortfolioAnalyzer:
    """Comprehensive portfolio analysis and metrics calculation"""
    
    def __init__(self, account: TradingAccount):
        self.account = account
        self.trades = Trade.objects.filter(
            account=account,
            close_time__isnull=False
        ).order_by('-close_time')
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get main portfolio metrics"""
        if not self.trades.exists():
            return self._empty_portfolio_data()
        
        # Basic metrics
        total_trades = self.trades.count()
        winning_trades = self.trades.filter(profit__gt=0).count()
        losing_trades = self.trades.filter(profit__lt=0).count()
        
        total_profit = self.trades.aggregate(Sum('profit'))['profit__sum'] or 0
        total_commission = self.trades.aggregate(Sum('commission'))['commission__sum'] or 0
        net_profit = total_profit + total_commission
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Average win/loss
        avg_win = self.trades.filter(profit__gt=0).aggregate(Avg('profit'))['profit__avg'] or 0
        avg_loss = self.trades.filter(profit__lt=0).aggregate(Avg('profit'))['profit__avg'] or 0
        
        # Profit factor
        gross_profit = self.trades.filter(profit__gt=0).aggregate(Sum('profit'))['profit__sum'] or 0
        gross_loss = abs(self.trades.filter(profit__lt=0).aggregate(Sum('profit'))['profit__sum'] or 0)
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        # Symbol statistics
        symbol_stats = self._get_symbol_statistics()
        
        # Recent trades
        recent_trades = self._get_recent_trades_data()
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 1),
            'total_profit': round(float(total_profit), 2),
            'total_commission': round(float(total_commission), 2),
            'net_profit': round(float(net_profit), 2),
            'avg_win': round(float(avg_win), 2),
            'avg_loss': round(float(avg_loss), 2),
            'profit_factor': round(float(profit_factor), 2),
            'total_volume': round(float(self.trades.aggregate(Sum('volume'))['volume__sum'] or 0), 2),
            'symbol_stats': symbol_stats,
            'recent_trades': recent_trades,
        }
    
    def get_advanced_analytics(self) -> Dict[str, Any]:
        """Get advanced analytics and metrics"""
        if not self.trades.exists():
            return {}
        
        # Calculate Sharpe ratio (simplified)
        daily_returns = self._calculate_daily_returns()
        sharpe_ratio = self._calculate_sharpe_ratio(daily_returns)
        
        # Maximum drawdown
        max_drawdown = self._calculate_max_drawdown()
        
        # Average trade duration
        avg_duration = self._calculate_average_duration()
        
        # Risk metrics
        var_95 = self._calculate_var(0.95)
        
        return {
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'avg_duration_hours': round(avg_duration, 1),
            'var_95': round(var_95, 2),
            'daily_returns': daily_returns[:30],  # Last 30 days
            'monthly_performance': self._get_monthly_performance(),
            'hourly_performance': self._get_hourly_performance(),
        }
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """Get risk management metrics"""
        if not self.trades.exists():
            return {}
        
        # Risk distribution
        risk_distribution = self._calculate_risk_distribution()
        
        # Position sizing analysis
        position_analysis = self._analyze_position_sizing()
        
        return {
            'risk_distribution': risk_distribution,
            'position_analysis': position_analysis,
            'risk_alerts': self._generate_risk_alerts(),
        }
    
    def _empty_portfolio_data(self) -> Dict[str, Any]:
        """Return empty portfolio structure"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_profit': 0,
            'total_commission': 0,
            'net_profit': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'total_volume': 0,
            'symbol_stats': [],
            'recent_trades': [],
        }
    
    def _get_symbol_statistics(self) -> List[Dict]:
        """Calculate statistics per symbol"""
        symbols = self.trades.values('symbol').distinct()
        symbol_stats = []
        
        for symbol_data in symbols:
            symbol = symbol_data['symbol']
            symbol_trades = self.trades.filter(symbol=symbol)
            
            total_profit = symbol_trades.aggregate(Sum('profit'))['profit__sum'] or 0
            total_trades = symbol_trades.count()
            winning_trades = symbol_trades.filter(profit__gt=0).count()
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            symbol_stats.append({
                'symbol': symbol,
                'trades': total_trades,
                'profit': round(float(total_profit), 2),
                'win_rate': round(win_rate, 1),
            })
        
        return sorted(symbol_stats, key=lambda x: x['profit'], reverse=True)
    
    def _get_recent_trades_data(self) -> List[Dict]:
        """Get recent trades for display"""
        recent_trades = self.trades[:20]  # Last 20 trades
        
        trades_data = []
        for trade in recent_trades:
            trades_data.append({
                'id': trade.trade_id,
                'symbol': trade.symbol,
                'side': trade.side,
                'volume': float(trade.volume),
                'open_price': float(trade.open_price),
                'close_price': float(trade.close_price or 0),
                'profit': round(float(trade.profit or 0), 2),
                'open_time': trade.open_time.strftime('%m/%d/%Y'),
                'close_time': trade.close_time.strftime('%m/%d/%Y') if trade.close_time else '',
            })
        
        return trades_data
    
    def _calculate_daily_returns(self) -> List[float]:
        """Calculate daily returns for risk metrics"""
        # Group trades by date and calculate daily P&L
        daily_pnl = {}
        
        for trade in self.trades:
            if trade.close_time:
                date = trade.close_time.date()
                if date not in daily_pnl:
                    daily_pnl[date] = 0
                daily_pnl[date] += float(trade.profit or 0)
        
        # Convert to returns list
        returns = list(daily_pnl.values())
        return sorted(returns)[-60:]  # Last 60 days
    
    def _calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio (simplified)"""
        if not returns or len(returns) < 2:
            return 0
        
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0
        
        # Assuming risk-free rate of 2% annually (simplified)
        risk_free_rate = 0.02 / 365  # Daily risk-free rate
        return (avg_return - risk_free_rate) / std_dev
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        cumulative_returns = []
        running_total = 0
        
        for trade in self.trades.order_by('close_time'):
            if trade.profit:
                running_total += float(trade.profit)
                cumulative_returns.append(running_total)
        
        if not cumulative_returns:
            return 0
        
        peak = cumulative_returns[0]
        max_drawdown = 0
        
        for value in cumulative_returns:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100 if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def _calculate_average_duration(self) -> float:
        """Calculate average trade duration in hours"""
        durations = [trade.duration_hours for trade in self.trades if trade.is_closed]
        return sum(durations) / len(durations) if durations else 0
    
    def _calculate_var(self, confidence_level: float) -> float:
        """Calculate Value at Risk"""
        returns = self._calculate_daily_returns()
        if not returns:
            return 0
        
        sorted_returns = sorted(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        return abs(sorted_returns[index]) if index < len(sorted_returns) else 0
    
    def _get_monthly_performance(self) -> List[Dict]:
        """Get monthly performance data"""
        monthly_data = {}
        
        for trade in self.trades:
            if trade.close_time and trade.profit:
                month_key = trade.close_time.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = 0
                monthly_data[month_key] += float(trade.profit)
        
        # Convert to list format for charts
        return [
            {'month': month, 'profit': round(profit, 2)}
            for month, profit in sorted(monthly_data.items())
        ]
    
    def _get_hourly_performance(self) -> Dict[int, float]:
        """Get performance by hour of day"""
        hourly_data = {hour: 0 for hour in range(24)}
        
        for trade in self.trades:
            if trade.close_time and trade.profit:
                hour = trade.close_time.hour
                hourly_data[hour] += float(trade.profit)
        
        return hourly_data
    
    def _calculate_risk_distribution(self) -> Dict[str, float]:
        """Calculate risk distribution"""
        low_risk = 0
        medium_risk = 0
        high_risk = 0
        
        for trade in self.trades:
            # Simple risk classification based on volume
            if float(trade.volume) <= 0.1:
                low_risk += 1
            elif float(trade.volume) <= 0.5:
                medium_risk += 1
            else:
                high_risk += 1
        
        total = self.trades.count()
        if total == 0:
            return {'low': 0, 'medium': 0, 'high': 0}
        
        return {
            'low': round(low_risk / total * 100, 1),
            'medium': round(medium_risk / total * 100, 1),
            'high': round(high_risk / total * 100, 1),
        }
    
    def _analyze_position_sizing(self) -> Dict[str, Any]:
        """Analyze position sizing patterns"""
        volumes = [float(trade.volume) for trade in self.trades]
        
        if not volumes:
            return {}
        
        return {
            'avg_volume': round(sum(volumes) / len(volumes), 2),
            'max_volume': max(volumes),
            'min_volume': min(volumes),
            'volume_consistency': round(self._calculate_volume_consistency(volumes), 2),
        }
    
    def _calculate_volume_consistency(self, volumes: List[float]) -> float:
        """Calculate volume consistency score"""
        if len(volumes) < 2:
            return 100
        
        avg_volume = sum(volumes) / len(volumes)
        variance = sum((v - avg_volume) ** 2 for v in volumes) / len(volumes)
        std_dev = variance ** 0.5
        
        # Return consistency as percentage (lower std dev = higher consistency)
        if avg_volume == 0:
            return 0
        
        cv = std_dev / avg_volume  # Coefficient of variation
        return max(0, 100 - (cv * 100))
    
    def _generate_risk_alerts(self) -> List[Dict[str, str]]:
        """Generate risk management alerts"""
        alerts = []
        
        # Check for overconcentration in single symbol
        symbol_stats = self._get_symbol_statistics()
        if symbol_stats:
            top_symbol = symbol_stats[0]
            if top_symbol['trades'] > self.trades.count() * 0.8:
                alerts.append({
                    'type': 'warning',
                    'message': f"High concentration in {top_symbol['symbol']} ({top_symbol['trades']} trades)"
                })
        
        # Check win rate
        total_trades = self.trades.count()
        if total_trades > 10:
            winning_trades = self.trades.filter(profit__gt=0).count()
            win_rate = winning_trades / total_trades * 100
            
            if win_rate < 40:
                alerts.append({
                    'type': 'danger',
                    'message': f"Low win rate: {win_rate:.1f}% - Review strategy"
                })
            elif win_rate > 70:
                alerts.append({
                    'type': 'success',
                    'message': f"Excellent win rate: {win_rate:.1f}%"
                })
        
        return alerts


# CSV Processor Class
class CSVTradeProcessor:
    """Process trading CSV files and import trades"""
    
    def __init__(self, account: TradingAccount):
        self.account = account
    
    def process_csv(self, csv_file) -> Dict[str, int]:
        """Process uploaded CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Map CSV columns to model fields
            column_mapping = {
                'ID': 'trade_id',
                'Symbol': 'symbol',
                'Side': 'side',
                'Volume': 'volume',
                'Open price': 'open_price',
                'Close Price': 'close_price',
                'Stop loss': 'stop_loss',
                'Take profit': 'take_profit',
                'Open time': 'open_time',
                'Close time': 'close_time',
                'Commission': 'commission',
                'Swap': 'swap',
                'Profit': 'profit',
                'Reason': 'reason'
            }
            
            processed = 0
            skipped = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Check if trade already exists
                    if Trade.objects.filter(
                        account=self.account,
                        trade_id=row.get('ID', '')
                    ).exists():
                        skipped += 1
                        continue
                    
                    # Create trade object
                    trade_data = self._map_row_to_trade(row, column_mapping)
                    if trade_data:
                        Trade.objects.create(account=self.account, **trade_data)
                        processed += 1
                    else:
                        skipped += 1
                        
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
            
            return {
                'processed': processed,
                'skipped': skipped,
                'errors': errors
            }
            
        except Exception as e:
            raise Exception(f"Error processing CSV: {str(e)}")
    
    def _map_row_to_trade(self, row, column_mapping) -> Dict[str, Any]:
        """Map CSV row to trade model fields"""
        try:
            trade_data = {}
            
            # Map basic fields
            for csv_col, model_field in column_mapping.items():
                if csv_col in row and pd.notna(row[csv_col]):
                    value = row[csv_col]
                    
                    if model_field in ['open_time', 'close_time']:
                        # Parse datetime
                        trade_data[model_field] = pd.to_datetime(value)
                    elif model_field in ['volume', 'open_price', 'close_price', 'stop_loss', 
                                       'take_profit', 'commission', 'swap', 'profit']:
                        # Convert to decimal
                        trade_data[model_field] = Decimal(str(value))
                    else:
                        trade_data[model_field] = str(value)
            
            # Validate required fields
            required_fields = ['trade_id', 'symbol', 'side', 'volume', 'open_price', 'open_time']
            for field in required_fields:
                if field not in trade_data:
                    return None
            
            return trade_data
            
        except Exception:
            return None

