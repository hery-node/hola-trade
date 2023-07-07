# hola-trade

## 项目的目的

本项目是为了搭建一个 python 的底层自动化量化交易的框架，对 QMT 提供的函数进行封装，方便使用。

同时搭建量化策略的模板实现，方便用户基于此模板进行模板的定制。

## 搭建开发环境

```
conda create --name trade python=3.9 -y
conda activate trade
pip install -r requirements.txt

```

## 发布到 PyPI

```
./publish.sh

```

## 安装使用

```
pip install hola-trade

```

## 如何使用

使用模板

```
from hola_trade.core.ctx import Context, Container, Bar
from hola_trade.trade.account import User
from hola_trade.trade.stock import Stock
from hola_trade.trade.policy import Policy
from hola_trade.trade.ratio import TrendRatioRule, Ratio
from hola_trade.trade.condition import Condition, PolicyConditions, Target

# setting for policy
policy_name = "Trade250"
user_id = "test"
# 调仓时间
adjust_time = "14:50:00"
# 最大持股数量
max_holdings = 10
# 单个股票的仓位占比
holding_ratio = 0.2
# 分几次建仓
batches = 2

# 仓位控制参数
# 深圳成分指数
main_code = "399001"
short_days = 5
mid_days = 10
long_days = 20
# 1线之上仓位
short_ratio = 0.2
# 2线之上仓位
mid_ratio = 0.5
# 3线之上仓位
long_ratio = 0.9

# 选股参数
# 中期均线天数
fast_days = 20
# 长期均线天数
slow_days = 250
# 观察股价低于长期均线的天数
watch_days = 20
# 观察期间低于长期均线的概率
watch_ratio = 0.8
# 量比
volume_ratio = 2
# 止盈目标
goal_rate1 = 20
goal_rate2 = 50
# 止损 12%
loss_rate = 12


container = Container(timetag_to_datetime, get_trade_detail_data, order_value, order_shares)
user = User.get_instance(user_id, container)
ratio_rule = TrendRatioRule(user, container, Ratio(max_holdings, holding_ratio), batches, main_code, Ratio(short_days, short_ratio), Ratio(mid_days, mid_ratio), Ratio(long_days, long_ratio))


class SelectCondition(Condition):
    def filter(self, bar: Bar, ctx: Context, user: User, codes: list[str]) -> list[Target]:
        # write your policy code here
        return []


class BuyCondition(Condition):
    def filter(self, bar: Bar, ctx: Context, user: User, codes: list[str]) -> list[Target]:
        # write your policy code here
        return []


class AddCondition(Condition):
    def filter(self, bar: Bar, ctx: Context, user: User,  codes: list[str]) -> list[Target]:
        # write your policy code here
        return []


class SellCondition(Condition):
    def filter(self, bar: Bar, ctx: Context, user: User, codes: list[str]) -> list[Target]:
        # write your policy code here
        return []


class ClearCondition(Condition):
    def filter(self, bar: Bar,  ctx: Context, user: User,  codes: list[str]) -> list[Target]:
        # write your policy code here
        return []


select_condition = SelectCondition()
buy_condition = BuyCondition()
add_condition = AddCondition()
sell_condition = SellCondition()
clear_condition = ClearCondition()
policy_conditions = PolicyConditions(select_condition, buy_condition, add_condition, sell_condition, clear_condition)

policy = Policy(policy_name, user, container, adjust_time, ratio_rule, policy_conditions)


def init(ContextInfo):
    pass


def handlebar(ContextInfo):
    ctx = Context(ContextInfo)
    policy.handle_bar(ctx)

```
