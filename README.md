<p align="center">
    <img src="resources/logo.png" alt="spyllm - AI Agent Observability Platform" width="400"/>
</p>
<h3 align="center" style="font-family: 'Fira Mono', Monospace;">spyllm</h3>
<h3 align="center" style="font-family: 'Fira Mono', Monospace;">Platform-Agnostic Agentic AI Runtime Observability Framework</h3>

<p align="center">
    <a href="https://github.com/cyberark/spyllm/commits/main">
        <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/cyberark/spyllm">
    </a>
    <a href="https://github.com/cyberark/spyllm">
        <img alt="GitHub code size" src="https://img.shields.io/github/languages/code-size/cyberark/spyllm">
    </a>
    <a href="https://github.com/cyberark/spyllm/blob/master/LICENSE">
        <img alt="Apache License" src="https://img.shields.io/github/license/cyberark/spyllm">
    </a>
    <a href="https://discord.gg/Zt297RAK">
        <img alt="Join Discord Community" src="https://img.shields.io/discord/1330486843938177157">
    </a>
</p>

## 🌟 Overview

spyllm is a cutting-edge observability framework designed to provide deep insights into AI agent interactions across diverse platforms and frameworks. By seamlessly intercepting, logging, and analyzing interactions, spyllm empowers developers to understand and optimize their AI-driven applications with unprecedented visibility.

<p align="center">
    <img src="resources/spyllm.gif" alt="spyllm Demonstration" width="800"/>
</p>

## ✨ Key Features

- **Comprehensive Interaction Tracking**: Monitor LLM and tool calls in real-time
- **Advanced Visualization**: Generate intuitive graphs for in-depth analysis
- **Detailed Metadata Capture**: Log tool inputs, arguments, and performance metrics
- **Multi-Framework Support**: Compatible with various AI development frameworks

## 🚀 Supported Frameworks

- Langgraph
- Autogen
- (More coming soon!)

## 📦 Prerequisites
To ensure compatibility with spyllm, your application must be written in Python. The visualization UI will be built locally on your endpoint using npm,
so make sure you have the following installed:

- Python 3.11+
- [poetry](https://python-poetry.org/)
- npm

## 🔧 Installation

Install spyllm directly from GitHub:

```bash
pip install git+https://github.com/cyberark/spyllm.git
```

## 🖥️ Quick Start

1. Import spyllm in your main module:
   ```python
   import spyllm
   ```

2. Ensure your entry point is within a `__main__` block:
   ```python
   if __name__ == "__main__":
       # Your code execution starts here
   ```

3. Launch the UI:
   ```bash
   spyllm ui
   # (Take note this will open a new tab in your browser)
   ```

Your AI agent interactions will now be automatically tracked and monitored!

## 📚 Documentation

For comprehensive guides and detailed usage instructions, visit our [GitHub Wiki](https://github.com/cyberark/spyllm/wiki).

## 🤝 Contributing

We welcome contributions! Please review our [CONTRIBUTING.md](https://github.com/cyberark/spyllm/blob/main/CONTRIBUTING.md) for guidelines on how to get involved.

## 📄 License

spyllm is released under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

## 📧 Contact

Have questions or suggestions? Reach out to us at [fzai@cyberark.com](mailto:fzai@cyberark.com) or join our [Discord Community](https://discord.gg/Zt297RAK).

## 🌈 Powered By CyberArk

A project from CyberArk, dedicated to advancing AI observability and security.