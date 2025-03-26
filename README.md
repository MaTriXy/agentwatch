<p align="center">
      <img src="resources/logo.png" alt="Project Logo" width="400" style="vertical-align:middle; margin-right:10px; font-family: 'Fira Mono', Monospace;" /><br/>
         <span align="center" style="font-family: 'Fira Mono', Monospace;">spyllm</span><br/>
        <span align="center" style="font-family: 'Fira Mono', Monospace;">a platform agnostic Agentic AI runtime observability framework</span><br/>
</p>
<p align="center">
<a href="https://github.com/cyberark/spyllm/commits/main">
   <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/cyberark/spyllm">
</a>
&nbsp;&nbsp;
<a href="https://github.com/cyberark/spyllm">
   <img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/cyberark/spyllm">
</a>
&nbsp;&nbsp;
<a href="https://github.com/cyberark/spyllm/blob/master/LICENSE">
   <img alt="GitHub License" src="https://img.shields.io/github/license/cyberark/spyllm">
</a>
&nbsp;&nbsp;
<a href="https://discord.gg/Zt297RAK">
   <img alt="Discord" src="https://img.shields.io/discord/1330486843938177157">
</a>

</p>
<br/>
<p align="center">
   <img alt="spyllmgif" src="resources/spyllm.gif" />
   <br/>
</p>

### What's it all about?
---

spyllm is a powerful observability framework designed to monitor and analyze AI agent interactions across different platforms and frameworks. It provides comprehensive insights into LLM-powered applications, helping developers understand and optimize their AI systems through detailed tracking and visualization of agent behaviors, conversations, and performance metrics.
Whether you use the vanilla OpenAI client or the full blown langgraph framework - spyllm knows how to seamlessly intercept, log, and analyze interactions, giving you full visibility into how your AI agents operate. With minimal integration effort, spyllm provides insights and drills down your flows, making it an essential tool for any AI-driven application.

### Prerequisites
---

Ensure you have the following installed:

- **npm**  
- **Python 3.11**  
- **Poetry**  

## Using spyllm
### Step 1: Add as a dependency to your project and import
Add spyllm as a dependency in your project:
```bash
pip install git+https://github.com/cyberark/spyllm.git # Or use any other package manager
```

### Step 2: Add an import to your main module
```python
import spyllm
```

### Step 3: Run the UI and launch your agent!
```bash
./run_ui.sh
```

Once the UI is running, all agent interactions will be tracked and monitored

That’s it! 🚀

## Documentation

Explore detailed usage instructions in the [Wiki](https://github.com/cyberark/spyllm/wiki).

## Examples


## Key Features

## Supported (and tested) frameworks

## Contributing

Contributions are welcome! If you would like to contribute to spyllm, please follow the guidelines outlined in the [CONTRIBUTING.md](https://github.com/cyberark/spyllm/blob/main/CONTRIBUTING.md) file.

## License

spyllm is released under the [Apache License](https://www.apache.org/licenses/LICENSE-2.0). See the [LICENSE](https://github.com/cyberark/spyllm/blob/main/LICENSE) file for more details.

## Contact

If you have any questions or suggestions regarding spyllm, please feel free to contact us at [fzai@cyberark.com](mailto:fzai@cyberark.com).

