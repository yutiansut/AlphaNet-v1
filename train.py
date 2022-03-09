# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 22:30:49 2022

@author: 30601
"""
import torch
from torch.utils.data import TensorDataset
from torch.utils.data import DataLoader
from d2l import torch as d2l 
from alphanet_v1 import alphanet
from torch import nn
# from pytorchtools import EarlyStopping
#导入数据
# 2207: 2083,half of year:125
X_all = torch.load(r"C:\Users\30601\Desktop\interp\量化\alphanet\stocks_data\002207.XSHE_pictures_x.pt").type(torch.FloatTensor)
Y_all = torch.load(r"C:\Users\30601\Desktop\interp\量化\alphanet\stocks_data\002207.XSHE_pictures_y.pt").type(torch.FloatTensor)

X = X_all[125:1500 + 125,:,:,:]
Y = Y_all[125:1500 + 125,].reshape(1500,1)
train_x = X[:950,:,:,:]
train_y = Y[:950,:]
test_data_x = X[950:,:,:,:]
test_data_y = Y[950:,:]

train_data = TensorDataset(train_x, train_y)
train_loader = DataLoader(
    dataset=train_data,
    batch_size=64,
    shuffle=True,
    num_workers=0
)

#start to train
def init_weights(m):
    if type(m) == nn.Linear:
        nn.init.trunc_normal_(m.weight)
device = d2l.try_gpu()
# RMSProp，0.0001

def train_net(alphanet,train_loader,test_data_x , test_data_y,lr = 0.001,times = 10):
    # from tensorboardX import SummaryWriter
    # logger = SummaryWriter(log_dir="C://Users//30601//Desktop//alphanet-v1//002207.XSHE//log3")
    alphanet.to(device)
    optimizer = torch.optim.RMSprop(alphanet.parameters(),lr = lr)
    loss_func = torch.nn.MSELoss()
    test_data_x , test_data_y = test_data_x.to(device), test_data_y.to(device)    
    # log_step_interval = 100 
    # timer = d2l.Timer()
    print('training on', device)
    loss0 = 0.1
    test_mse0 = 1
    for epoch in range(200):
        if epoch > 120: 
            optimizer = torch.optim.RMSprop(alphanet.parameters(),lr = 0.0001)  
         # print("epoch:", epoch)
         # 每一轮都遍历一遍数据加载器 
        for step, (x, y) in enumerate(train_loader):
             # 前向计算->计算损失函数->(从损失函数)反向传播->更新网络
             # timer.start() #计时
             optimizer.zero_grad()   # 清空梯度（可以不写）
             x, y = x.to(device), y.to(device)
             predict = alphanet(x)
             loss = loss_func(predict,y)
             loss.backward()     # 反向传播计算梯度
             optimizer.step()    # 更新网络
             # timer.stop()
             # global_iter_num = epoch * len(train_loader) + step + 1  # 计算当前是从训练开始时的第几步(全局迭代次数)
             # if global_iter_num % log_step_interval == 0:
        if epoch< 3 or epoch > 98:
            test_predict = alphanet(test_data_x)
            test_mse = loss_func(test_predict,test_data_y) 
             # # 在测试集上预测并计算mse
             # # 添加的第一条日志：损失函数-全局迭代次数
             # logger.add_scalar("train loss", loss.item() ,global_step=global_iter_num)
             # # 添加第二条日志：mes-全局迭代次数
             # logger.add_scalar("test_mse", test_mse.item(), global_step=global_iter_num)
             # for name, param in alphanet.named_parameters():
                 # logger.add_histogram(name, param.data.cpu().numpy(), global_step=global_iter_num)
         # 控制台输出一下
            print("epoch:{}, train_mse:{:.2},test_mse:{:.2}".format(epoch + 1, loss.item(), test_mse.item()))
            if loss < loss0 and test_mse < test_mse0:
                loss0 = loss
                test_mse0 = test_mse
                print('save model')
                torch.save(alphanet.state_dict(), 
                           "C://Users//30601//Desktop//alphanet-v1//002207.XSHE//第二个半年//model_param{}.pth".format(times)) 
                        
     # print("global_step:{}, loss:{:.2},test_mse:{:.2}".format(global_iter_num, loss.item(), test_mse.item()))

for i in range(0,10):
    print('第{}次训练'.format(i+1))
    alphanetv1 = alphanet
    alphanetv1.apply(init_weights) #初始化参数
    train_net(alphanetv1,train_loader,test_data_x , test_data_y,lr = 0.001,times = i + 1)                                                                
#保存
# torch.save(alphanet.state_dict(), "C://Users//30601//Desktop//alphanet-v1//002207.XSHE//model_param1.pth")
# alphanet.load_state_dict(torch.load("C://Users//30601//Desktop//alphanet-v1//002207.XSHE//model_param2.pth") )
