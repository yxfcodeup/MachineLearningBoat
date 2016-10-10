# Spark集群安装记录
***
### 安装前设置
系统为centos-7-x86_64  
1. 若是GNOME桌面环境，且为中文目录，执行以下命令将目录更改为英文目录，  
```
$ export LANG=en_US  
$ xdg-user-dirs-update  
$ export LANG=zh_CN.UTF-8  
```

2. 网络设置  
分别更改集群hostname为master , slave1 , slave2 ，也可以用其他名字代表，可以修改文件/etc/hostname，也可以使用命令    
```
$ hostnamectl set-hostname master (注：CentOS 7原有的修改hosts方法无效了)  
$ vim /etc/hosts  
192.168.1.131 master  
192.168.1.132 slave1  
192.168.1.133 slave2  
```
静态ip配置：  
```
$ vim /etc/sysconfig/network-scripts/ifcfg-eno16777736  
TYPE="Ethernet"
BOOTPROTO="none"
DEFROUTE="yes"
IPV4_FAILURE_FATAL="no"
NAME="eno16777736"
UUID="017163bc-203c-49bb-83c4-a9892b8fbaa3"
DEVICE="eno16777736"
ONBOOT="yes"
IPADDR="192.168.1.130"
PREFIX="24"
GATEWAY="192.168.1.1"
DNS1="8.8.8.8"
```
关闭防火墙：  
```
$ systemctl status firewalld.service（查看防火墙状态）  
$ systemctl stop firewalld.service（关闭防火墙）  
$ systemctl enable firewalld.service（永久关闭防火墙）  
```
3. 检测SSH是否安装，如果没有则安装SSH  
4. 创建hadoop用户（为管理方便）  
```
$ useradd hadoop      创建用户名为hadoop的用户  
```
5. 配置SSH无密钥登陆  
下面是在master上的操作，  
```
$ su hadoop  
$ ssh-keygen -t rsa -P ''
$ cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys  
$ chmod 600 ~/.ssh/authorized_keys  
$ su  
$ vim /etc/ssh/sshd_config  
RSAAuthentication yes #启用RSA认证
PubkeyAuthentication yes #启用公钥私钥配对认证方式
AuthorizedKeysFile .ssh/authorized_keys #公钥文件路径
$ su hadoop
$ scp ~/.ssh/id_rsa.pub hadoop@slave1:~/  
$ scp ~/.ssh/id_rsa.pub hadoop@slave2:~/  
```
下面是在slave1和slave2上的操作，  
```
$ su hadoop  
$ mkdir ~/.ssh/ #没有则执行此句，或者直接ssh-keygen -t rsa -P ''
$ chmod 700 ~/.ssh  
$ cat ~/id_rsa.pub >> ~/.ssh/authorized_keys  
$ chmod 600 ~/.ssh/authorized_keys  
$ su
$ vim /etc/ssh/sshd_config  
RSAAuthentication yes #启用RSA认证  
PubkeyAuthentication yes #启用公钥私钥配对认证方式  
AuthorizedKeysFile .ssh/authorized_keys #公钥文件路径  
```
***
### 安装必须的软件  
1. 安装JDK（安装1.8在使用maven编译hadoop时会出错）
```
$ Chmod –R 777 /opt/
$ tar -zxvf jdk-7u79-linux-x64.tar.gz -C /opt/
$ mv jdk1.7.0_79/ java
$ vim /etc/profile     
#加入以下内容
export JAVA_HOME=/opt/java
export JRE_HOME=${JAVA_HOME}/jre  
export CLASSPATH=.:${JAVA_HOME}/lib:${JRE_HOME}/lib  
export PATH=${JAVA_HOME}/bin:$PATH
#再用以下命令配置默认JDK版本
$ update-alternatives --install /usr/bin/java java /usr/opt/java/bin/java 300
$ update-alternatives --install /usr/bin/javac javac /opt/java/bin/javac 300
$ update-alternatives --install /usr/bin/jar jar /opt/java/bin/jar 300   
$ update-alternatives --install /usr/bin/javah javah /opt/java/bin/javah 300
$ update-alternatives --install /usr/bin/javap javap /opt/java/bin/javap 300
$ update-alternatives --config java
```
2. 安装其他相关软件
```
$ yum install maven svn ncurses-devel gcc* lzo-devel zlib-devel autoconf automake libtool cmake openssl-devel
```
3. 安装ant（不重新编译hadoop不用3~5步骤）
```
$ tar zxvf apache-ant-1.9.5-bin.tar.gz –C /opt/
$ vim /etc/profile
export ANT_HOME=/opt/apache-ant-1.9.5
export PATH=$PATH:$ANT_HOME/bin
```
4. 安装findbugs  
```
$ tar zxvf findbugs-3.0.0.tar.gz –C /opt/
$ vim /etc/profile
export FINDBUGS_HOME=/opt/findbugs-3.0.0
export PATH=$PATH:$FINDBUGS_HOME/bin
```
5. 安装protobuf  
```
$ tar zxvf protobuf-2.5.0.tar.gz(必须是2.5.0版本的，不然编译hadoop的时候报错)
$ cd protobuf-2.5.0
$ ./configure --prefix=/usr/local
$ make && make install
```
***
### 编译hadoop源码（未完成）  
```
$ tar zxvf hadoop-2.6.0-src.tar.gz
$ cd hadoop-2.6.0-src
$ mvn package -Pdist,native,docs -DskipTests -Dtar
```
1. maven中央仓库的配置（增加访问速度，视具体情况选择）
```
$ vim /usr/share/maven/conf/setting.xml
<settings>
	<localRepository>D:\maven_new_repository</localRepository>
</settings>
```
***
### 配置hadoop  
1. 基础操作  
```
$ tar -zxvf hadoop-2.6.0-x64.tar.gz -C /opt/
$ chown -R hadoop:hadoop /opt/hadoop-2.6.0
$ vi /etc/profile
export HADOOP_HOME=/opt/hadoop-2.6.0
export PATH=$PATH:$HADOOP_HOME/bin
$ su hadoop
$ cd /opt/hadoop-2.6.0
$ mkdir -p dfs/name
$ mkdir -p dfs/data
$ mkdir -p tmp
$ cd etc/hadoop
```
2. 配置所有slave节点
```
$ vim slaves
master  
slave1  
slave2  
```
3. 修改hadoop-env.sh和yarn-env.sh
```
export JAVA_HOME=/opt/java
export HADOOP_ROOT_LOGGER=DEBUG,console
```
4.修改core-site.xml
```
<configuration>
	<property>
		<name>fs.defaultFS</name>
		<value>hdfs://master:9000</value>
	</property>
	<property>
		<name>io.file.buffer.size</name>
		<value>131702</value>
	</property>
	<property>
		<name>hadoop.tmp.dir</name>
		<value>file:/opt/hadoop-2.6.0/tmp</value>
	</property>
<!--
	<property>
		<name>hadoop.proxyuser.hadoop.hosts</name>
		<value>*</value>
	</property>
	<property>
		<name>hadoop.proxyuser.hadoop.groups</name>
		<value>*</value>
	</property>
	<property>
		<name>hadoop.native.lib</name>
		<value>false</value>
	</property>
-->
</configuration>
```
5. 修改hdfs-site.xml
```
<configuration>
	<property>
		<name>dfs.namenode.name.dir</name>
		<value>file:/opt/hadoop-2.6.0/dfs/name</value>
	</property>
	<property>
		<name>dfs.datanode.data.dir</name>
		<value>file:/opt/hadoop-2.6.0/dfs/data</value>
	</property>
	<property>
		<name>dfs.replication</name>
		<value>3</value>
	</property>
	<property>
		<name>dfs.namenode.secondary.http-address</name>
		<value>master:9001</value>
	</property>
	<property>
		<name>dfs.webhdfs.enabled</name>
		<value>true</value>
	</property>
</configuration>
```
6. 修改mapred-site.xml
```
<configuration>
	<property>
		<name>mapreduce.framework.name</name>
		<value>yarn</value>
	</property>
	<property>
		<name>mapreduce.jobhistory.address</name>
		<value>master:10020</value>
	</property>
	<property>
		<name>mapreduce.jobhistory.webapp.address</name>
		<value>master:19888</value>
	</property>
</configuration>
```
7. 修改yarn-site.xml
```
<configuration>
<!-- Site specific YARN configuration properties -->
	<property>
		<name>yarn.nodemanager.aux-services</name>
		<value>mapreduce_shuffle</value>
	</property>
	<property>
		<name>yarn.resourcemanager.hostname</name>
		<value>master</value>
	</property>
	<property>
		<name>yarn.resourcemanager.address</name>
		<value>master:8032</value>
	</property>
	<property>
		<name>yarn.resourcemanager.scheduler.address</name>
		<value>master:8030</value>
	</property>
	<property>
		<name>yarn.resourcemanager.resource-tracker.address</name>
		<value>master:8031</value>
	</property>
	<property>
		<name>yarn.resourcemanager.admin.address</name>
		<value>master:8033</value>
	</property>
	<property>
		<name>yarn.resourcemanager.webapp.address</name>
		<value>master:8088</value>
	</property>
<!--
	<property>
		<name>yarn.nodemanager.resource.memory-mb</name>
		<value>3000</value>
	</property>
-->
</configuration>
```
8. 格式化namenode
需要先将hadoop目录分发到各个节点  
```
$ scp -r HADOOP_HOME hadoop@slave1:/opt/
$ scp -r HADOOP_HOME hadoop@slave2:/opt/
$ HADOOP_HOME/bin/hadoop namenode -format
```
只需要在master上执行一次就行  
9. 启动hdfs  
```
$ HADOOP_HOME/sbin/start-dfs.sh
$ HADOOP_HOME/sbin/start-yarn.sh
```
10. 检查启动情况  
可以在流浪器里输入网址http://master的ip地址:8080，或者http://master的ip地址:50070查看，也可以在命令行里使用jps命令查看，master上会有NameNode,ResourceManager,DataNode,NodeManager,SecondaryNameNode几个进程，slave上会有NodeManager,DataNode进程  
11. 问题及日志
```
$ HADOOP_HOME/logs
```
***
### 安装spark  
```
#spark-1.4.1-bin-hadoop2.6.tgz
$ tar –zxvf spark-1.4.1-bin-hadoop2.6.tgz –C /opt/
$ cd /opt/ spark-1.4.1-bin-hadoop2.6/conf
$ cp slaves.template slaves
$ cp spark-env.sh.template spark-env.sh
$ vim spark-env.sh
export SPARK_HOME=/opt/ spark-1.4.1-bin-hadoop2.6
export MASTER=spark://master:7077
export SPARK_MASTER_IP=192.168.1.55:
$ vim slaves  
master  
slave1  
slave2  
```
然后同步到各个节点  
启动spark  
```
$ SPARK_HOME/sbin/start-master.sh
$ SPARK_HOME/sbin/start-slaves.sh
（或者SPARK_HOME/sbin/start-all.sh）
```
***
### 参考资料
[CentOS7-64bit 编译 Hadoop-2.5.0，并分布式安装](http://my.oschina.net/u/1428349/blog/313646#OSC_h2_1)
***
### 常见问题及补充  
1. 在使用maven的时候，如果是jdk1.8，将会报错  
2. 在配置spark时,若各个节点的hostname与/etc/hosts文件中的映射名不一样的话,也会报错,这时,只要export MASTER=以及export SPARK_MASTER_IP=就行  
3. 各节点间的jdk以及Python版本需保持一致,否则会导致错误
4. 报错: mkdir: Cannot create directory /user/tk. Name node is in safe mode.  
使用命令：./hadoop dfsadmin -safemode leave  
