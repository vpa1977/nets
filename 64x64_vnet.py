# create vnet protobuf

import caffe
from caffe import layers as L
from caffe import params as P
from dicom_helper import netset

batch_size = 1
size = 64
depth = 32 

def get_filler():
	return dict([('type' , 'msra'), ('variance_norm' , 2)])

def make_conv(data, outputs, kernel_size, pad, stride):
	conv = L.Convolution( data,  
				num_output = outputs, kernel_size = kernel_size, pad=pad, stride=stride, 
				weight_filler =get_filler(), 
				bias_filler=dict([('type', 'constant'), ('value', 0)]), 
				param=[{"lr_mult":1, "decay_mult":1},{"lr_mult":2, "decay_mult":0}])
	return conv

def make_tiles(n, data):
	n_splits = 16 
	result = netset(n, "split", L.Split(data, ntop = n_splits))
	tiles =  netset(n, "merge", L.Concat( *	result, axis = 1))
	conv = make_conv(data, n_splits, 5,2, 1)
	eltwise = L.Eltwise(tiles, conv, operation = P.Eltwise.SUM)	
	prelu = L.PReLU(eltwise, in_place=True)
	return n_splits, prelu;

def max_pool(bottom, ks, stride=1, pad=1):
	return L.Pooling(bottom, pool=P.Pooling.MAX, kernel_size=ks, stride=stride, pad=1)

def left_branch(data, width, iters):
	input = data
	for i in range(0, iters-1):
		conv = make_conv(input , width, 5, 2, 1)
		input = L.PReLU(conv, in_place= True)
#	input = max_pool(input,3)
	input = make_conv(input , width, 5, 2, 1)
	return input

def make_downsample(n, width, iters, data):
	conv = make_conv(data, width, 2, 0, 2)
	prelu = L.PReLU(conv, in_place= True)
# left
	conv = left_branch(prelu, width, iters)
	
	eltwise = L.Eltwise(prelu, conv, operation = P.Eltwise.SUM)
	netset(n, "elementwise_down_"+str(width), eltwise)	
	return L.PReLU(eltwise, in_place=True)


def upsample_merge(n,data, to_upsample, width, iters):
	deconv = L.Deconvolution( to_upsample, convolution_param=dict( num_output=width,kernel_size=2, stride=2, weight_filler =get_filler(), 
				bias_filler=dict([('type', 'constant'), ('value', 0)])), 
				param=[{"lr_mult":1, "decay_mult":1},{"lr_mult":2, "decay_mult":0}])
	prelu = L.PReLU(deconv)
	concat =  L.Concat(data, prelu)
	netset(n, "concat_up_"+str(width), concat)	

	left = left_branch(concat, width*2, iters)
	netset(n, "left_branch_up_"+str(width), left)	
	
	eltwise = L.Eltwise(concat, left, operation = P.Eltwise.SUM)	
	netset(n, "elementwise_up_"+str(width), eltwise)	
	return L.PReLU(eltwise, in_place=True)

def create_net():
	n = caffe.NetSpec()
	n.data = L.Input( shape = dict(dim=[batch_size, 1, size,size, depth ]) )
	n.label = L.Input( shape = dict(dim=[batch_size, 1, size,size, depth ]) )
	n_splits , n.tiles = make_tiles(n, n.data)
	


	n.first_downsample = make_downsample(n,n_splits*2, 1,  n.tiles)
	n.second_downsample = make_downsample(n, n_splits*4, 2,  n.first_downsample)
	n.third_downsample = make_downsample(n, n_splits*8, 3,  n.second_downsample)
	n.fourth_downsample = make_downsample(n, n_splits*16, 3,  n.third_downsample)

	n.concat_0 = upsample_merge(n,n.third_downsample, n.fourth_downsample, n_splits *8, 3)
	n.concat_1 = upsample_merge(n,n.second_downsample, n.concat_0, n_splits *4 , 2)
#	n.concat_1 = upsample_merge(n,n.second_downsample, n.third_downsample, n_splits *4 , 2)
	n.concat_2 = upsample_merge(n,n.first_downsample, n.concat_1, n_splits*2, 1)
	n.concat_3 = upsample_merge(n,n.tiles, n.concat_2, n_splits, 1)

	conv = left_branch(n.concat_3, 2, 2)
	netset(n, "output", conv)
	reshaped = L.Reshape( conv, reshape_param={'shape':{'dim': [0, 2, size * size * depth]}})
	softmax = L.Softmax(reshaped)
	n.flat_label = L.Reshape(n.label, reshape_param={'shape':{'dim': [0, 1, size * size * depth]}})
	n.flat_image = L.Reshape(n.data, reshape_param={'shape':{'dim': [0, 1, size * size * depth]}})
	n.loss = L.Python(softmax,n.flat_image ,  n.flat_label, name  = "loss",  loss_weight = 1,  python_param={'module': 'multi_hinge', 'layer': 'MultiHingeLayer'})

	return n.to_proto()


net = create_net()

f = open("sample.prototxt", "w");
f.write(str(net))
f.close()
print(net)
instance = caffe.Net("sample.prototxt", caffe.TRAIN)
instance.forward()
print("test done")
