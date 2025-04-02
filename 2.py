import matplotlib.pyplot as plt

# 数据
acl_labels = ['ACL1', 'ACL2', 'ACL3', 'ACL4', 'ACL5', 'ACL6']
proposed_method = [0.7943, 0.7619, 0.7983, 0.7834, 0.8048, 0.8012]
proposed_method_without_gcbp = [0.6760, 0.5595, 0.6901, 0.7067, 0.7404, 0.7398]

# 绘制折线图
plt.figure(figsize=(10, 6))
plt.plot(acl_labels, proposed_method, marker='o', label='Proposed method')
plt.plot(acl_labels, proposed_method_without_gcbp, marker='s', label='Proposed method without GCBP')

# 添加标题和标签

plt.xlabel('ACL')
plt.ylabel('Values')
plt.ylim(0.5, 0.85)
plt.grid(True)
plt.legend()

# 保存图表
plt.savefig('comparison_results_acl.png')

# 显示图表
plt.show()
