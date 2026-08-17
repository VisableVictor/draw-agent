# Vue 3 CDN 交互模式参考

当页面需要交互功能（折叠面板、进度条、移动端菜单等）时，推荐使用 Vue 3 CDN。

```html
<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
```

## 基础模板结构

```html
<div id="app" v-cloak>
    <!-- HTML 内容 -->
</div>

<script>
const { createApp, ref } = Vue;
createApp({
    setup() {
        const isOpen = ref(false);
        const items = ref([...]);
        return { isOpen, items };
    }
}).mount('#app');
</script>
```

## 常见交互模式

### 折叠面板

```html
<div v-show="isOpen" v-cloak>隐藏内容</div>
```

配合 `<transition name="fade">` 实现淡入淡出动画。

### 移动端菜单

```html
<button @click="mobileMenu = !mobileMenu">菜单</button>
<transition name="fade">
    <div v-show="mobileMenu">菜单内容</div>
</transition>
```

### 列表数据驱动

```html
<div v-for="item in items" :key="item.id">{{ item.name }}</div>
```

### 复选框组 + 进度计算

```html
<input type="checkbox" v-model="item.checked" @change="updateProgress">
<span>{{ checkedCount }}/{{ totalCount }}</span>
```

## 最佳实践

1. **折叠面板** - 默认收起，点击展开，节省页面空间
2. **进度条** - 用 CSS `transition` 实现平滑动画
3. **移动端菜单** - 汉堡按钮切换，点击链接后自动关闭
4. **复选框组** - 数据集中管理，自动计算完成进度
5. **动画过渡** - 使用 `<transition name="fade">` 实现淡入淡出
