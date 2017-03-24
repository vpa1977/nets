import caffe
from caffe import layers as L
from caffe import params as P



def netset(n, nm, l):
	setattr(n, nm, l);
	return getattr(n,nm);
# pad 1 - no borders, pad 0 - borders and enable crop
def conv_relu(n, name, bottom, nout, ks, stride=1, pad=1, group=1, 
              batchnorm=False, weight_filler=dict(type='xavier')):
	conv = netset(n, 'conv'+name, L.Convolution(bottom, kernel_size=ks, stride=stride, 
												num_output=nout, pad=pad, group=group, 
												weight_filler=weight_filler))
	convbatch=conv;
	if batchnorm:
		batchnorm = netset(n, 'bn'+name, L.BatchNorm(conv, in_place=True, 
													param=[{"lr_mult":0},{"lr_mult":0},{"lr_mult":0}]));
		convbatch = batchnorm
	# Note that we don't have a scale/shift afterward, which is different from
	# the original Batch Normalization layer.  Using a scale/shift layer lets
	# the network completely silence the activations in a given layer, which
	# is exactly the behavior that we need to prevent early on.
	relu=netset(n, 'relu'+name, L.ReLU(convbatch, in_place=True))
	return  relu 

def conv_sigmoid(n, name, bottom, nout,ks, stride=1, pad=0, group=1, 
              batchnorm=False, weight_filler=dict(type='xavier')):
	conv = netset(n, 'conv'+name, L.Convolution(bottom, kernel_size=ks, stride=stride, 
												num_output=nout, pad=pad, group=group, 
												weight_filler=weight_filler))
	convbatch=conv;
	if batchnorm:
		batchnorm = netset(n, 'bn'+name, L.BatchNorm(conv, in_place=True, 
													param=[{"lr_mult":0},{"lr_mult":0},{"lr_mult":0}]));
		convbatch = batchnorm
	# Note that we don't have a scale/shift afterward, which is different from
	# the original Batch Normalization layer.  Using a scale/shift layer lets
	# the network completely silence the activations in a given layer, which
	# is exactly the behavior that we need to prevent early on.
	relu=netset(n, 'sigmoid'+name, L.Sigmoid(convbatch, in_place=True))
	return  relu 

def max_pool(bottom, ks, stride=1):
	return L.Pooling(bottom, pool=P.Pooling.MAX, kernel_size=ks, stride=stride, pad=0)

def unet_conv_layer(n, name, input,  outputs, kernel_size):
	relu0 = conv_relu(n, name + '_fc',input,  outputs, kernel_size )
	relu1 = conv_relu(n, name + '_sc',relu0,  outputs, kernel_size )
	return relu1, max_pool(relu1, 2)

def unet_upsample(n, name, input_upsample, input_conv, outputs, ks = 3, upsample_size =2, stride=1, pad=0, group=1, weight_filler=dict(type='xavier')):
	deconv = netset( n, 'deconv' + name, L.Deconvolution( input_upsample,  convolution_param=dict(num_output=outputs,kernel_size=2, stride=1)))
#	crop = netset(n, 'crop' + name, L.Crop(input_conv,deconv))
	concat = netset(n, 'concat' + name, L.Concat(deconv, input_conv))
	relu0 = conv_relu(n, name + '_subconv',concat,  outputs, ks )
	return  conv_relu(n, name + '_subconv',relu0,  outputs, ks)
	

def get_unet():
	n = caffe.NetSpec()
	n.input, n.label = L.Python( name  = "loaddata", ntop = 2 ,  python_param={'module': 'slice_image', 'layer': 'SliceImages', 'param_str': '"\'do_test\': 0"'})
#	n.input, n.label = L.Python( name  = "loaddata", ntop = 2 ,  python_param={'module': 'slice_image', 'layer': 'SliceImages', 'param_str': '"\'do_test\': 1"'}, include=dict(phase=caffe.TEST))
	relu1, n.maxpool1 = unet_conv_layer(n, 'conv1', n.input, 32, 3)
	relu2, n.maxpool2 = unet_conv_layer(n, 'conv2', n.maxpool1, 64, 3)
	relu3, n.maxpool3 = unet_conv_layer(n, 'conv3', n.maxpool2, 128, 3)
	relu4, n.maxpool4 = unet_conv_layer(n, 'conv4', n.maxpool3, 256, 3)
	
	_relu5 = conv_relu(n, 'conv5_0',n.maxpool4, 512, 3)
	relu5 = conv_relu(n, 'conv5_1',  _relu5, 512, 3)

	upsample6 = unet_upsample(n, 'upsample6',relu5, relu4, 256,3 )

	upsample7 = unet_upsample(n, 'upsample7',upsample6, relu3, 128,3)

	upsample8 = unet_upsample(n, 'upsample8',upsample7, relu2, 64,3)

	upsample9 = unet_upsample(n, 'upsample9',upsample8, relu1, 32,3)
	scoreRelu = conv_relu(n, 'score', upsample9, 1, 1,pad=0)

	n.loss_layer = L.SoftmaxWithLoss(scoreRelu, n.label)


	return n.to_proto()


print(get_unet())	