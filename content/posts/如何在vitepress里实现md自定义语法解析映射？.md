+++
title = '如何在vitepress里实现md自定义语法解析映射？'
date = '2026-01-08T18:18:10+08:00'
draft = false
+++
![Pasted image 20251228172816.png](/images/Pasted image 20251228172816.png)
## 如何自定义解析md语法？
在.vitepress\config\index.mts里可以看到markdown的相关配置
``` typescript
   markdown: {
      config: (md) => mdPlugin(md),
    },
```
进入.vitepress\config\plugins.ts可以看到myPlugin的定义，其实就是使用到了markdown-it-container这个库去匹配和映射成我们想要映射的Demo.vue组件
``` typescript
export const mdPlugin = (md: MarkdownRenderer) => {
  //...省略其他代码
  md.use(mdContainer, 'demo', createDemoContainer(md))
}
```
再进入createDemoContainer，在.vitepress\plugins\demo.ts里可以看到createDemoContainer方法的详情，其实就是解析传入md进行匹配带:::demo开头的字符，匹配到就进行Demo组件的映射，注意这里使用到了encodeURIComponent ，主要是为了防止md.render()直接作为属性时在Demo组件进行html解析时可能会导致的错误，使用encodeURIComponent就让内容解析成%xxx的格式，即排除掉"<>等这种会导致标签/属性解析问题的符号 
```typescript
function createDemoContainer(md: MarkdownRenderer): ContainerOpts {

  return {

    validate(params) {

      return !!params.trim().match(/^demo\s*(.*)$/)

    },
    render(tokens, idx) {

      const m = tokens[idx].info.trim().match(/^demo\s*(.*)$/)

      if (tokens[idx].nesting === 1 /* means the tag is opening */) {

        const description = m && m.length > 1 ? m[1] : ''

        const sourceFileToken = tokens[idx + 2]

        let source = ''

        const sourceFile = sourceFileToken.children?.[0].content ?? ''

        if (sourceFileToken.type === 'inline') {

          source = fs.readFileSync(

            path.resolve(docRoot, 'examples', `${sourceFile}.vue`),

            'utf-8'

          )
        }

        if (!source) throw new Error(`Incorrect source file: ${sourceFile}`)

  

        return `<Demo source="${encodeURIComponent(

          md.render(`\`\`\` vue\n${source}\`\`\``)

        )}" path="${sourceFile}" raw-source="${encodeURIComponent(

          source

        )}" description="${encodeURIComponent(md.render(description))}">

  <template #source><ep-${sourceFile.replaceAll('/', '-')}/></template>`

      } else {

        return '</Demo>\n'

      }

    },

  }
}
```
那现在我们具备md的自定义解析映射了，该如何让vitepress更自动的导入我们想要映射的Demo组件呢？
## 如何更自动化引入组件？
在.vitepress\config\index.mts可以看到关于vite插件的配置`vite: getViteConfig(configEnv)` ，进入.vitepress\config\vite.ts查看getViteConfig，可以看到element-plus里其实是将关于vitepress的自定义主题组件都定义在了.vitepress/vitepress/components里，然后配置了unplugin-vue-components插件去自动全局引入这些组件
```typescript 
export const getViteConfig = ({ mode }: { mode: string }): ViteConfig => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    // ...其他配置
    plugins: [
      // ...其他配置
      // https://github.com/antfu/unplugin-vue-components
      Components({
        dirs: ['.vitepress/vitepress/components'],

        allowOverrides: true,

        // custom resolvers
        resolvers: [
          // auto import icons
          // https://github.com/antfu/unplugin-icons
          IconsResolver(),
        ],

        // allow auto import and register components used in markdown
        include: [/\.vue$/, /\.vue\?vue/, /\.md$/],
      }),
    ],
  }
}
```