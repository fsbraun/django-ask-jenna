const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');


const distribution = {
    admin: 'static/ask_jenna/',
};

module.exports = {
    entry: {
        admin: './private/js/admin.ask_jenna.js',
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: (pathData) => {
                return distribution[pathData.chunk.name] + 'css/bundle.' + pathData.chunk.name + '.min.css';
            },
        }),
    ],
    module: {
        rules: [
            {
                test: /skin\.css$/i,
                use: [MiniCssExtractPlugin.loader, 'css-loader'],
            },
            {
                test: /content\.css$/i,
                use: ['css-loader'],
            },
            {
                test: /ckeditor5-[^/\\]+[/\\]theme[/\\]icons[/\\][^/\\]+\.svg$/,
                use: ['raw-loader']
            },
            {
                test: /ckeditor5-[^/\\]+[/\\]theme[/\\].+\.css$/,

                use: [
                    {
                        loader: 'style-loader',
                        options: {
                            injectType: 'singletonStyleTag',
                            attributes: {
                                'data-cke': true
                            }
                        }
                    },
                ]
            },
            {
                test: /\.css$/,
                exclude: /ckeditor5.*\.css$/,
                use: [MiniCssExtractPlugin.loader, 'css-loader'],
            },
            {
                test: /\.(s[ac]ss)$/i,
                use: [MiniCssExtractPlugin.loader, 'css-loader', 'sass-loader'],
            },
            {
                test: /\.js$/,
                enforce: "pre",
                use: ["source-map-loader"],
            },

            // {
            //     test: /\.js$/,
            //     use: [{
            //         loader: 'babel-loader',
            //         options: {
            //             presets: ['es2015']
            //         }
            //     }],
            // },
            // {
            //     test: /\.ts$/,
            //     use: [{
            //         loader: 'ts-loader',
            //         options: {
            //             compilerOptions: {
            //                 declaration: false,
            //                 target: 'es5',
            //                 module: 'commonjs'
            //             },
            //             transpileOnly: true
            //         }
            //     }]
            // },
            // {
            //     test: /\.svg$/,
            //     use: [{
            //         loader: 'html-loader',
            //         options: {
            //             minimize: true
            //         }
            //     }]
            // }
        ]
    },
    optimization: {
        minimizer: [new CssMinimizerPlugin()],
    },

    output: {
        path: path.resolve(__dirname, 'ask_jenna/'),
        filename: (pathData) => {
            return distribution[pathData.chunk.name] + 'bundles/bundle.' + pathData.chunk.name + '.min.js';
        }
    },
    mode: 'production',
    devtool: 'source-map',
    // By default, webpack logs warnings if the bundle is bigger than 200kb.
    performance: {hints: false}
};
