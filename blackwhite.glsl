#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif

uniform sampler2D texture;
uniform vec2 texOffset;

varying vec4 vertColor;
varying vec4 vertTexCoord;


void round_col(in float in_col, in float num, in float out_col){
    out_col = round(in_col * num) / num;
}

void round_color(in vec4 in_color, in float num_color, out vec4 out_color){
    round_col(in_color.x, num_color, out_color.x);
    round_col(in_color.y, num_color, out_color.y);
    round_col(in_color.z, num_color, out_color.z);
    out_color.w = 1.0;
}

void main() {
    int lines = 1000;
    int bLine = 5;
    int num_col = 16;

    float x = vertTexCoord.x;
    float y = vertTexCoord.y - 0.5;
    float h = 0.5;
    vec2 _pos = vertTexCoord.xy + vec2(0, y*h*x*(x-1)/5);
    vec4 col = vec4(0.0, 0.0, 0.0, 1.0);

    if(0.0 <= _pos.x && _pos.x <= 1.0 && 0.0 <= _pos.y && _pos.y <= 1.0){
        col = texture2D(texture, _pos.xy);
    }

    if(mod(vertTexCoord.y * lines, bLine) >= 1){
        round_color(col, num_col, col);
        gl_FragColor = col * vec4(0.8, 1.0, 0.8, 1.0);
    }
    else{
        gl_FragColor = vec4(0, 0, 0, 1.0);
    }
}